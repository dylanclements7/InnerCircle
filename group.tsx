import { useState } from "react"

import "./styles.css" // Only import once

export default function Group({ name, emotionList, nameList }) {
  console.log(nameList)
  return (
    <>
      <div className="group-content">
        <div className="group-name">{name}</div>
        <div className="emoji-group">
          {emotionList.map((emoji, index) => (
            <>
            <div className="emoji-name-pair">
            <div key={index} className="emoji">
                {emoji}
            </div>

             <div className="nameList">
                {nameList[index]}
            </div>
            </div>
            </>
          ))}
        </div>
      </div>
    </>
  )
}
