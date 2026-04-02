
/*
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.google.adk.samples.agents.firestorerunner;

import java.util.Scanner;
import java.util.logging.Logger;
import com.google.adk.agents.RunConfig;
import com.google.adk.sessions.FirestoreSessionService;
import com.google.adk.events.Event;
import com.google.adk.runner.FirestoreDatabaseRunner;
import com.google.adk.sessions.Session;
import com.google.cloud.firestore.Firestore;
import com.google.cloud.firestore.FirestoreOptions;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import com.google.adk.agents.BaseAgent;
import com.google.adk.tools.Annotations.Schema;
import java.util.Map;
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.FunctionTool;
import static java.nio.charset.StandardCharsets.UTF_8;

/**
 * The FirestoreRunner class serves as an entry point for running Firestore-related operations.
 * This class can be expanded to include methods for initializing Firestore,
 * performing CRUD operations, and handling Firestore events.       
 */

public final class FirestoreRunner {
    
    private static final Logger logger = Logger.getLogger(FirestoreRunner.class.getName());
    private static final String APP_NAME = "time-agent";
    public static void main(String[] args) {
    
        logger.info("Starting FirestoreRunner...");

        RunConfig runConfig = RunConfig.builder().build();

        BaseAgent timeAgent = initAgent(APP_NAME);

        // Use try-with-resources for Firestore and Scanner to ensure automatic resource cleanup
        try (Firestore firestore = FirestoreOptions.getDefaultInstance().getService();
             Scanner scanner = new Scanner(System.in, UTF_8)) {
            
            // Use FirestoreDatabaseRunner to persist session state
            FirestoreDatabaseRunner runner = new FirestoreDatabaseRunner(
                    timeAgent,
                    APP_NAME,
                    firestore
            );

            // Create a new session
            String userId = "user-" + System.currentTimeMillis();
            String sessionId = "session-" + System.currentTimeMillis();

            Session session = new FirestoreSessionService(firestore)
                    .createSession(APP_NAME, userId, null, sessionId)
                    .blockingGet();

            while (true) {
                System.out.print("\nYou > ");
                String userInput = scanner.nextLine();
                if ("quit".equalsIgnoreCase(userInput) || "exit".equalsIgnoreCase(userInput)) {
                    break;
                }

                Content userMsg = Content.fromParts(Part.fromText(userInput));
                Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg, runConfig);

                System.out.print("\nAgent > ");
                events.blockingForEach(event -> {
                    if (event.finalResponse()) {
                        System.out.println(event.stringifyContent());
                    }
                });
            }
        } catch (Exception e) {
            logger.severe("An error occurred: " + e.getMessage());
        }

        logger.info("FirestoreRunner finished execution.");
    }

    /** Mock tool implementation */
    @Schema(description = "Get the current time for a given city")
    public static Map<String, String> getCurrentTime(
        @Schema(name = "city", description = "Name of the city to get the time for") String city) {
        return Map.of(
            "city", city,
            "forecast", "The time is 10:30 am."
        );
    }
    
    /**
     * Initialize the agent with tools and configuration.
     * @return An initialized {@link BaseAgent}.
     */
     protected static  BaseAgent initAgent(String agentName) {
        return LlmAgent.builder()
            .name(agentName)
            .description("Tells the current time in a specified city")
            .instruction("""
                You are a helpful assistant that tells the current time in a city.
                Use the 'getCurrentTime' tool for this purpose.
                """)
            .model("gemini-2.5-flash")
            .tools(FunctionTool.create(FirestoreRunner.class, "getCurrentTime"))
            .build();
    }
}
