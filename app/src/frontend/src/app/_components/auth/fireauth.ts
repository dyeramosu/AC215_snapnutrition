import {
    GoogleAuthProvider,
    signInWithPopup,
} from "firebase/auth";

import { auth } from "@/app/_components/auth/firebase"


export async function signInWithGoogle() {
    const provider = new GoogleAuthProvider();

    try {
        await signInWithPopup(auth, provider);
    } catch (error) {
        console.error("Error signing in with Google", error);
    }
}

export async function signOut() {
    try {
        return auth.signOut();
    } catch (error) {
        console.error("Error signing out with Google", error);
    }
}
