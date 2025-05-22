import React from "react";
import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Box,
    Stack,
    Link
   
} from "@mui/material"

function Navbar(){
    return (
        <AppBar position="sticky" color="primary">
            <Toolbar disableGutters>
                <Typography
                 variant="h6"
                 component={Link}
                 to="/"
                 sx={{
                    flexGrow:1,
                    textDecoration:"none",
                    color:"inherit",
                    fontWeight:"bold"
                 }}
                >
                    Kiran's Picserve
                </Typography>
                <Stack direction="row" spacing={2}>
                    <Button color="inherit" component={Link} to="/">Home</Button>
                    <Button color="inherit" component={Link} to="/gallery"> Gallery</Button>
                </Stack>
                <Box sx={{ml:"auto"}}>
                    <Button
                        variant="contained"
                        color="secondary"
                        component={Link}
                        to="/admin-login"
                        sx={{ml:2}}
                    >Admin Login</Button>
                </Box>
            </Toolbar>
        </AppBar>
    )
}
export default Navbar;