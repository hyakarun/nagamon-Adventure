import { showHomeScreen, showLoginScreen, showRegisterScreen } from './screens.js';
import { auth } from './firebase-init.js';
import { GoogleAuthProvider, signInWithPopup, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.12.4/firebase-auth.js";

// --- DOM Elements ---
const googleLoginButton = document.getElementById('google-login-button');
const loginButton = document.getElementById('login-button');
const registerButton = document.getElementById('register-button');
const showRegisterLink = document.getElementById('show-register-link');
const showLoginLink = document.getElementById('show-login-link');

// --- Event Listeners ---

// Google Login
if (googleLoginButton) {
    googleLoginButton.addEventListener('click', async () => {
        const provider = new GoogleAuthProvider();
        try {
            const result = await signInWithPopup(auth, provider);
            await handleSuccessfulLogin(result.user);
        } catch (error) {
            handleLoginError(error);
        }
    });
}

// Email/Password Registration
if (registerButton) {
    registerButton.addEventListener('click', async () => {
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;

        if (!username || !email || !password) {
            alert("すべての項目を入力してください。");
            return;
        }

        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            // 新規登録時はバックエンドにusernameも送信
            await handleSuccessfulLogin(userCredential.user, username);
        } catch (error) {
            handleLoginError(error);
        }
    });
}

// Email/Password Login
if (loginButton) {
    loginButton.addEventListener('click', async () => {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        if (!email || !password) {
            alert("メールアドレスとパスワードを入力してください。");
            return;
        }

        try {
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            await handleSuccessfulLogin(userCredential.user);
        } catch (error) {
            handleLoginError(error);
        }
    });
}

// --- Screen Switching ---
if (showRegisterLink) {
    showRegisterLink.addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterScreen();
    });
}

if (showLoginLink) {
    showLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        showLoginScreen();
    });
}


// --- Helper Functions ---

async function handleSuccessfulLogin(user, username = null) {
    const idToken = await user.getIdToken();
    const body = { idToken };
    if (username) {
        body.username = username;
    }

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        const data = await response.json();

        if (response.ok) {
            console.log("バックエンドログイン成功:", data.username);
            showHomeScreen();
        } else {
            console.error("バックエンドログイン失敗:", data.message);
            alert("ログインに失敗しました: " + data.message);
        }
    } catch (error) {
        console.error("バックエンドへの送信エラー:", error);
        alert("サーバーとの通信に失敗しました。");
    }
}

function handleLoginError(error) {
    const errorCode = error.code;
    const errorMessage = error.message;
    console.error("認証エラー:", errorCode, errorMessage);

    let displayMessage = `認証に失敗しました。(${errorCode})`; // エラーコードを表示
    if (errorCode === 'auth/email-already-in-use') {
        displayMessage = "このメールアドレスは既に使用されています。";
    } else if (errorCode === 'auth/wrong-password') {
        displayMessage = "パスワードが間違っています。";
    } else if (errorCode === 'auth/user-not-found') {
        displayMessage = "このメールアドレスのユーザーは見つかりません。";
    } else if (errorCode === 'auth/weak-password') {
        displayMessage = "パスワードは6文字以上で入力してください。";
    }
    alert(displayMessage);
}