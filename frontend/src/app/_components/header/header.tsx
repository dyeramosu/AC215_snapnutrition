import { AppBar, Box, Button, IconButton, Link, Menu, Toolbar, Typography } from "@mui/material";
import MenuIcon from '@mui/icons-material/Menu';
import { auth } from "@/app/_components/auth/firebase";
import { signInWithGoogle, signOut } from "@/app/_components/auth/fireauth";
import { useAuthState } from "react-firebase-hooks/auth";
import NextLink from "next/link";

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
                        <MenuIcon/>
                    </IconButton>
                    <Typography variant="h6" component="div" sx={{flexGrow: 1}}>
                        {user?.displayName}
                    </Typography>
                    <Button color={"inherit"} LinkComponent={NextLink} href={"/"}>Home</Button>
                    <Button color={"inherit"} LinkComponent={NextLink} href={"/calorie-counter"}>Calorie
                        Counter</Button>

                    {loginButton}
                </Toolbar>
            </AppBar>
        </Box>

    )
}