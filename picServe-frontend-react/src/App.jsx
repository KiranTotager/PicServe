import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Login from './pages/loginPage'
import Register from './pages/RegisterPage'
import Navbar from './pages/navBar'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
    <Navbar/>
     {/* <Login/> */}
     <Register />
    </>
  )
}

export default App
