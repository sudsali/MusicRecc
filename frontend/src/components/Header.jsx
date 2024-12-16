import React from "react";
import {ReactComponent as Logo} from "../assets/pipinstall.svg";
import { useNavigate } from "react-router-dom";

import "../App.css";

export function Header() {
    const navigate = useNavigate();
    const handleClick = () => {
        navigate("/", {replace : true})
    }
    return (
        <div className="Header">
            <button className="header-button" onClick={handleClick}>
                <Logo className="pipinstall-logo"/>
                <h1 style={{color: "white"}}>Pipinstall.</h1>
            </button>
        </div>
    )
}