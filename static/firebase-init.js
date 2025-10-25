import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.4/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.12.4/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyCr4ItrZzSLe_n_BW5W3vtTIngDpDBrrE0",
  authDomain: "adventure-game-1c116.firebaseapp.com",
  projectId: "adventure-game-1c116",
  storageBucket: "adventure-game-1c116.firebasestorage.app",
  messagingSenderId: "1048272340633",
  appId: "1:1048272340633:web:b759ec09c734bf4a3d5a08",
  measurementId: "G-9PLELE7Y39"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
