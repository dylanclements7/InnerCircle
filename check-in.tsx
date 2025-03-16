import { useEffect, useState } from "react"

import EPick from "~emoji-selector"
import './styles.css';
export default function CheckIn({
  currentEmotion,
  setCurrentEmotion,
  setView
}) {
  const [openPicker, setOpen] = useState(false)
  return (
    <>
      {!openPicker && (
        <div className="check-in">
          <p>How are you feeling?</p>
          <div className="select-emoji-button" onClick={() => setOpen(true)}>
            <p>{currentEmotion}</p>
          </div>
          <div className="center-view-button">
            <div className="view-groups-button"
              onClick={() => {
                setView(0)
              }}>
              View Groups
            </div>
          </div>
        </div>
      )}
      {openPicker && (
        <EPick
          setOpen={setOpen}
          setCurrentEmotion={(emotion) => {
            setCurrentEmotion(emotion.native)
          }}
        />
      )}
    </>
  )
}
