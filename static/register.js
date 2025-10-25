import { showHomeScreen } from './screens.js';
import { auth } from './firebase-init.js';
import { GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/10.12.4/firebase-auth.js";

const googleLoginButton = document.getElementById('google-login-button');

// Google Login Button Event Listener
if (googleLoginButton) {
    googleLoginButton.addEventListener('click', async () => {
        const provider = new GoogleAuthProvider();
        try {
            const result = await signInWithPopup(auth, provider);
            const idToken = await result.user.getIdToken();

            // Send ID token to backend
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ idToken: idToken }),
            });

            const data = await response.json();

            if (response.ok) {
                console.log("バックエンドログイン成功:", data.username);
                // player.name = data.username; // player.name will be updated in home.js
                showHomeScreen();
            } else {
                console.error("バックエンドログイン失敗:", data.message);
                alert("ログインに失敗しました: " + data.message);
            }

        } catch (error) {
            const errorMessage = error.message;
            console.error("Googleログインエラー:", errorMessage);
            alert("Googleログインに失敗しました: " + errorMessage);
        }
    });
}
