import React from "react";
import Login from "../components/Login";
import Wrapped from "../components/Wrapped";
import { AtmosphericBackground } from "../components/ui/atmospheric-background";

import {
    createBrowserRouter,
    createRoutesFromElements,
    Route,
    Routes,
    useLocation
  } from "react-router-dom";

function AnimatedRoutes() {
    const location = useLocation();
    return (
        <AtmosphericBackground>
            <Routes>
                <Route path="/" element={<Login/>}/>
                <Route path="/wrapped" element={<Wrapped/>}/>
            </Routes>
        </AtmosphericBackground>
    )
}

export default AnimatedRoutes;