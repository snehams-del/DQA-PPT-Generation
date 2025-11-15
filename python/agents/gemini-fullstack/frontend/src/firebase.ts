// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBZLU_BBUpSI-yZ-Y40vALGCIoNgMCfPV4",
  authDomain: "vantage-proof-prod.firebaseapp.com",
  projectId: "vantage-proof-prod",
  storageBucket: "vantage-proof-prod.firebasestorage.app",
  messagingSenderId: "115998949524",
  appId: "1:115998949524:web:3e0bf1fc533c9eddc27481",
  measurementId: "G-VEP7QEBBJF"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);