"use-client";
import { Header } from "./Header";
import "../App.css";
import { replace, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

export function Wrapped() {
    const navigate = useNavigate();
	const [getLoading, setLoading] = useState(false);
    const data = JSON.parse(window.sessionStorage.getItem("results"));

    useEffect(() => {
        if (!data) {
            navigate("/", {replace : true})
        }
    }, [data, navigate])
	
	const handleLogout = () => {
		navigate("/", {replace : true});
	}
	const handleClick = async () => {
		try {
			setLoading(true);
			const response = await fetch(`http://localhost:8000/api/report/${data.user_id}`);
			const reportData = await response.json();
			// Create and download report
			const blob = new Blob([reportData.report], { type: 'text/plain' });
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `music_report_${data.user_id}.txt`;
			document.body.appendChild(a);
			a.click();
			window.URL.revokeObjectURL(url);
			setLoading(false);
		} catch (error) {
			setLoading(false);
			console.error('Error downloading report:', error);
		}
	};
	
    return ((<div>
    	<Header/>
        <div className="wrapped-container">
			<div style={{height: "auto", width: "100%", display: "flex", justifyContent: "space-between"}}>
				<h2 style={{fontStyle: "normal", marginTop: "0px", fontSize: "32px", color: "white"}}>Your Music Wrapped! {data.name}</h2>
				<button className="logout-button" onClick={handleLogout} value="Log Out">Logout</button>
			</div>
			<div className="first-row">
				<div className="doublecard">
					<div className="top-all">
						<div className="top-content" style={{borderRight: "dashed 1px white"}}>
							<p style={{margin: "16px"}}>Top Songs</p>
							<ol className="ordered-list" style={{marginLeft: "24px"}}>
								{data.top_songs.map(song => <li>{song.title}</li>)}
							</ol>
						</div>
						<div className="top-content">
							<p style={{margin: "16px"}}>Top Artists</p>
							<ol className="ordered-list" style={{marginLeft: "24px"}}>
								{data.top_artists.map(artist => <li>{artist.name}</li>)}
							</ol>
						</div>
					</div>
				</div>
				<div className="doublecard" style={{padding: "16px"}}>
					<p style={{margin: "16px"}}>Wanna try something new? Here are some recommendations</p>
					<ol className="ordered-list" style={{padding: "0 24px"}}>
						{data.recommendations && data.recommendations.map((track, index) => (
							<li key={index} className="two-row-list">
								<p>{track.title}</p>
								<p>{track.artist}</p>
							</li>
						))}
					</ol>
				</div>
			</div>
			<div className="second-row">
				<div className="singlecard">
					<p>You've listened for</p>
					<p>{data.stats.total_listens} minutes</p>
				</div>
				<div className="singlecard">
					<p>{data.main_character_energy.split('-')[0]}</p>
				</div>

				<div className="singlecard">
					<p>You listen to {data.main_character_energy.split('\n')[1].split(':')[1].toLowerCase()} music the most! </p>
				</div>

				<div className="singlecard">
					<p>You played {data.stats.total_songs} songs</p>
					<p>so far</p>
				</div>
			</div>
			<div className="match-card-container">
			<div className="match-card">
				<p>We've found you some company</p>
				{data && data.similar_users ? (
					<>
						<p style={{fontSize: "36px"}}>
							{data.similar_users[0]?.name || "No match found"}
						</p>
						<p style={{fontSize: "18px", marginTop: "auto"}}>
							{data.similarity_reason}
						</p>
					</>
				) : (
					<p>Finding your musical soulmate...</p>
				)}
			</div>



			</div>
			<div style={{display: "flex", flexDirection: "column", justifyContent:"right", marginTop: "18px", paddingBottom: "48px", height: "100%"}}>
			<button className="button-custom" style={{position: "relative"}} onClick = {handleClick}>Download Full Report</button>
			<div className={"loading-bar-container" + getLoading? " first-load": ""} style={{transform: "translate(0, 16px)", overflow: "hidden", opacity: 0}}>
				<div className={"loading-bar " + (getLoading? "animate-in-slow" : "animate-out")}></div>
			</div>
			</div>
		</div>
    </div>)
    )
}

export default Wrapped;