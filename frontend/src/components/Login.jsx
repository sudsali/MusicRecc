import React from "react";
import { Header } from "./Header";
import "../App.css";
import { replace, useNavigate } from "react-router-dom";

import { useState, useEffect } from "react";

export function Login() {
    const [getName, setName] = useState('');
    const [getID, setID] = useState('');
    const [getError, setError] = useState(0);
    const [getLoading, setLoading] = useState(false);

    const navigate = useNavigate();
    useEffect(() => {
        window.sessionStorage.clear();
    })

    function validateID() {
        if (getID >= 5000 || getID < 0 || getID % 1 != 0 || !getID) {
            throw new Error ("Invalid ID");
        }
    }

    const url = "http://localhost:8000"
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            console.log(`Got ID ${getID}`)
            validateID();
            const response = await fetch(`${url}/api/user/${getID}`);
            
            if (response.ok) {
                const data = await response.json();
                if (getName.toLowerCase() != data.name.toLowerCase()) {
                    throw new Error("Names don't match");
                }
                window.sessionStorage.setItem("results", JSON.stringify(data));
                navigate('/wrapped', { replace:true });
            }
        } catch (error) {
            setLoading(false);
            setError(1);
            console.error('Error:', error);
        }
    };
    const  handleName = (event) => {
        setError(0);
        setName(event.target.value);
    };
    const  handleID = (event) => {
        setError(0);
        setID(event.target.value);
    };
    return (
        (<div>
            <Header/>
            <div className="login-card">
                <h2 style={{marginTop: "56px", fontSize: "32px", color: "white"}}>Let's get you started</h2>
                <div style={{display: "flex", flexDirection: "column", justifyContent: "space-between", height: "100%"}}>
                    <form style={{height: "100%"}} onSubmit={handleSubmit}>
                        <label>
                            Name
                            <p style={{margin: "0px", marginBottom: "8px", fontSize: "16px", color: "white"}}>Name</p>
                            <input className="input-field" type="text" value={getName} onChange={handleName}/>
                        </label>
                        <label>
                            ID
                            <p style={{margin: "0px", marginTop: "32px", marginBottom: "8px", fontSize: "16px", color: "white"}}>ID</p>
                            <input className="input-field" type="number" value={getID} onChange={handleID} />
                        </label>
                        <p className="error-text" style={{opacity: (getError*100)}}>Something's not right</p>
                        <div style={{marginTop: "16px"}}>
                            <button type="submit" value = "Submit" className="button-custom">Submit</button>
                            <div className="loading-bar-container first-load">
                                <div className={"loading-bar " + (getLoading? "animate-in" : "animate-out")}></div>
                            </div>
                        </div> 
                    </form>
                </div>
            </div>
          </div>)
    )
}

export default Login;