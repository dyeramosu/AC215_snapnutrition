// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyCU4rQ4AcCgiQujbTQUGQm3OHFiShVPCFg",
    authDomain: "csci-115-398800.firebaseapp.com",
    projectId: "csci-115-398800",
    storageBucket: "csci-115-398800.appspot.com",
    messagingSenderId: "551792351994",
    appId: "1:551792351994:web:ffde1967fabb653b884743",
    measurementId: "G-SDKL9V18GE"
};

// Initialize Firebase
export const firebaseApp = initializeApp(firebaseConfig);
export const auth = getAuth(firebaseApp);
