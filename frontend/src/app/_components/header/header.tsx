import { AppBar, Box, Button, IconButton, Toolbar, Typography } from "@mui/material";
import { auth } from "@/app/_components/auth/firebase";
import { signInWithGoogle, signOut } from "@/app/_components/auth/fireauth";
import { useAuthState } from "react-firebase-hooks/auth";
import NextLink from "next/link";
import { DinnerDining } from "@mui/icons-material";

export default function Header() {

    const [user, loading, error] = useAuthState(auth);

    let loginButton = <Button color="inherit" onClick={signInWithGoogle}>Login</Button>
    if (user?.displayName) {
        loginButton = <Button color="inherit" onClick={signOut}>Signout</Button>;
    }


    return (
        <Box sx={{flexGrow: 1, padding: "50px"}}>
            <AppBar>
                <Toolbar>
                    <IconButton
                        size="large"
                        edge="start"
                        color="inherit"
                        aria-label="menu"
                        sx={{mr: 2}}
                    >
                        <DinnerDining/>
                    </IconButton>
                    <Typography variant="h6" component="div" sx={{flexGrow: 1}}>
                        {user?.displayName}
                    </Typography>
                    <Button color={"inherit"} LinkComponent={NextLink} href={"/"}>Home</Button>
                    <Button color={"inherit"} LinkComponent={NextLink} href={"/calorieCounter"}>Calorie
                        Counter</Button>

                    {loginButton}
                </Toolbar>
            </AppBar>
        </Box>

    )
}
