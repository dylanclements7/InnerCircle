import { useEffect, useState } from "react"

import "./styles.css"

import Group from "~group"

export default function GroupView({
  setView,
  activeGroup,
  setActiveGroup,
  group,
  updateGroup
}) {
  const [isDropdownVisible, setDropdownVisible] = useState(false)
  const rightGroup = () => {
    const g = activeGroup + 1 > group.length - 1 ? 0 : activeGroup + 1
    setActiveGroup(g)
  }
  const leftGroup = () => {
    const g = activeGroup - 1 < 0 ? group.length - 1 : activeGroup - 1
    setActiveGroup(g)
  }
  const toggleMenu = () => {
    setDropdownVisible(!isDropdownVisible)
  }

  useEffect(() => {
    console.log("GROUP ________UPDATED")
    if (group && group.length > 0 && group[activeGroup] && group[activeGroup].users) {
      console.log(group[activeGroup].users)
    }
    updateGroup()
  }, [])
  
  // Add this before the return statement
  if (!group || group.length === 0 || !group[activeGroup]) {
    return <div className="group-view">Loading group data...</div>
  }

  return (
    <div className="group-view">
      <div onClick={leftGroup} className="group-button">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width={32}
          height={32}
          viewBox="0 0 32 32">
          <path
            fill="currentColor"
            d="M16 3C8.832 3 3 8.832 3 16s5.832 13 13 13s13-5.832 13-13S23.168 3 16 3m0 2c6.087 0 11 4.913 11 11s-4.913 11-11 11S5 22.087 5 16S9.913 5 16 5m1.78 4.28l-6 6l-.686.72l.687.72l6 6l1.44-1.44L13.937 16l5.28-5.28z"></path>
        </svg>
      </div>
      <Group
        name={group[activeGroup].name}
        emotionList={group[activeGroup].emotions}
        nameList={group[activeGroup].users}
      />

      <div onClick={rightGroup} className="group-button">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width={32}
          height={32}
          viewBox="0 0 32 32">
          <path
            fill="currentColor"
            d="M16 3C8.832 3 3 8.832 3 16s5.832 13 13 13s13-5.832 13-13S23.168 3 16 3m0 2c6.087 0 11 4.913 11 11s-4.913 11-11 11S5 22.087 5 16S9.913 5 16 5m-1.78 4.28l-1.44 1.44L18.064 16l-5.282 5.28l1.44 1.44l6-6l.686-.72l-.687-.72z"></path>
        </svg>
      </div>

      {/* Hamburger Menu */}
      <div className="hamburger-menu">
        <div className="hamburger-button">
            <button className="hamburger-icon" onClick={toggleMenu}>
            &#9776; {/* Hamburger icon */}
            </button>
        </div>
        {/* Dropdown Menu */}
        {isDropdownVisible && (
          <div className="dropdown-menu">
            <ul>
              <li
                onClick={() => {
                  setView(1)
                }}>
                <a>Set Emotion</a>
              </li>
              <li
                onClick={() => {
                  setView(2)
                }}>
                <a>Manage Groups</a>
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
