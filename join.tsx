import React, { useState } from "react"

import "./styles.css" // Ensure this file exists

const fs = require("fs")

export default function Join({ setView }) {
  const [name, setName] = useState("")
  const [password, setPassword] = useState("")
  const [submissionResult, setSubmission] = useState("")
  const link = "http://140.232.178.49:8080/create_user"

  const getData = async () => {
    const data = {
      user_name: name,
      password: password
    }

    try {
      const response = await fetch(link, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
      })
      const jsonData = await response.json()
      console.log("Response from server:", jsonData)
      return jsonData
    } catch (err) {
      console.error("Error:", err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const response = await getData()
    console.log("_______RIJGDVIS")
    console.log(response)
    const success = response.success
    if (!success) {
      setSubmission("Error making account")
    } else {
      const token = response.token
      localStorage.setItem("token", token)
      setView(2)
    }
  }

  return (
    <div className="j-big-class">
      <h2>Join</h2>
      <form onSubmit={handleSubmit} className="j-form">
        <label className="j-label">Enter your name:</label>
        <div className="j-input-name">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name"
            className="j-input-input"
          />
        </div>

        <label className="j-password">Enter your password:</label>
        <div className="j-input-password">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Your password"
            className="j-password-password"
          />
        </div>
        <p>{submissionResult}</p>
        <button type="submit" className="j-submit">
          Submit
        </button>
      </form>
    </div>
  )
}
