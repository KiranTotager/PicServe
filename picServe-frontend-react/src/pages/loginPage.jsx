import React, { useState } from "react";
import{
    Box,
    Button,
    Container,
    TextField,
    Typography,
    Avatar,
    Paper,
    IconButton,
    InputAdornment,
    Grid
} from "@mui/material";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
function Login(){
    const [showPassword,setShowPassword]=useState(false);
    return(
        <Container maxWidth="sm">
            <Paper elevation={6} sx={{
                mt:8,
                p:4,
                display:'flex',
                flexDirection:'column',
                alignItems:'center',
                borderRadius:3,
            }}>
                <Avatar sx={{m:1,bgcolor:'primary.main'}}>
                    <LockOutlinedIcon/>
                </Avatar>
                <Typography variant="h5" component="h1" gutterBottom>
                    Sign In
                </Typography>
                <Box component="form" sx={{mt:1,width:'100%'}} >
                    <TextField 
                    margin="normal"
                    fullWidth
                    label="Username"
                    autoComplete="text"
                    required
                    />
                    <TextField
                    margin="normal"
                    fullWidth
                    label="password"
                    type={showPassword?"text":"password"}
                    autoComplete="current-password"
                    required
                    InputProps={{
                        endAdornment:(<InputAdornment position="end">
                          <IconButton onClick={()=>setShowPassword(!showPassword)}>
                          {showPassword?<VisibilityOff/>:<Visibility/>}
                          </IconButton>
                            
                        </InputAdornment>)
                    }}
                    />
                    <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    sx={{mt:3,mb:2}} 
                    >
                        Sign In
                    </Button>
                </Box>
                <Grid container>
                    <Grid item xs>
                        <Button size="small">Forgot password?</Button>
                    </Grid>
                </Grid>
                <Typography variant="body2" align="center" sx={{mt:4}}>
                    Don't have an account ? <Button size="small">Sign Up</Button>
                </Typography>
            </Paper>

        </Container>
    )
}
export default Login;
