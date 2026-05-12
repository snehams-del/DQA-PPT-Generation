# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import json
from fastapi.testclient import TestClient
from google.genai import Client
from google.genai import types

# Ensure parent directory is in path to find backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.api.main import app

client = TestClient(app)

def load_dataset():
    with open("tests/eval/golden_dataset.json", "r") as f:
        return json.load(f)

def judge_response(extracted_text, expected_specs):
    # Initialize client (assumes credentials in environment)
    client = Client()
    
    prompt = f"""
    You are an expert judge evaluating the accuracy of extracted specifications against ground truth.
    
    Expected Specifications (Ground Truth):
    {json.dumps(expected_specs, indent=2)}
    
    Extracted Text:
    {extracted_text}
    
    Rate the accuracy of the extracted text compared to the ground truth on a scale of 0.0 to 1.0.
    Provide a score and a short justification.
    Format your response as a JSON object with keys 'score' (float) and 'justification' (string).
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {"score": 0.0, "justification": f"Failed during judgment: {e}"}

def evaluate():
    dataset = load_dataset()
    if not dataset:
        print("Dataset is empty.")
        return

    results = []

    for i, entry in enumerate(dataset):
        prompt = entry["prompt"]
        expected_url = entry["expected_url"]
        
        print(f"\nEvaluating Case {i+1}: {prompt}")
        session_id = f"eval_session_{i}"
        
        try:
            # Step 1: Find URL
            response = client.post(
                "/api/chat", 
                json={
                    "message": prompt,
                    "session_id": session_id,
                    "user_id": "eval_user"
                }
            )
            
            status_code = response.status_code
            resp_json = response.json()
            resp_text = resp_json.get("response", "")
            
            print(f"Status: {status_code}")
            print(f"Agent Response: {resp_text[:100]}...")
            
            url_found = expected_url in resp_text
            print(f"Expected URL Found: {url_found}")
            
            results.append({
                "prompt": prompt,
                "status_code": status_code,
                "url_found": url_found,
                "agent_response": resp_text
            })
            
            if url_found:
                print("Triggering Step 2: Extract Specs")
                response2 = client.post(
                    "/api/chat", 
                    json={
                        "message": "Yes, please extract details.",
                        "session_id": session_id,
                        "user_id": "eval_user"
                    }
                )
                resp_text2 = response2.json().get("response", "")
                print(f"Agent Response Step 2: {resp_text2[:200]}...")
                
                results[-1]["step2_response"] = resp_text2
                
                # Judge
                print("Judging extracted specs...")
                expected_specs = entry.get("expected_specs", {})
                judge_result = judge_response(resp_text2, expected_specs)
                print(f"Judge Score: {judge_result.get('score')}")
                print(f"Judge Justification: {judge_result.get('justification')}")
                
                results[-1]["judge_result"] = judge_result
            
        except Exception as e:
            print(f"Error evaluating case {i+1}: {e}")
            results.append({
                "prompt": prompt,
                "error": str(e)
            })

    # Summary
    print("\n=== Evaluation Summary ===")
    success_count = sum(1 for r in results if r.get("url_found", False))
    total_count = len(results)
    print(f"Successful URL Extractions: {success_count}/{total_count}")
    
    avg_score = 0.0
    scores = [r["judge_result"]["score"] for r in results if "judge_result" in r and "score" in r["judge_result"]]
    if scores:
        avg_score = sum(scores) / len(scores)
    print(f"Average Judge Score: {avg_score:.2f}")
    
    # Save results
    with open("tests/eval/eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to tests/eval/eval_results.json")

if __name__ == "__main__":
    evaluate()
