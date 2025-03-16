import { useState } from "react"

import Group from "~group"
import GroupCreator from "~group-creater"
import GroupForm from "~group-form"

export default function GroupManager({ groupList, setGroupList, setView }) {
  const [inCreator, setInCreator] = useState(false)
  return (
    <>
          {!inCreator && ( 
        <div className="group-manager">
          <div className="group-selector">
            <GroupForm
              setInCreator={(val) => {
                setInCreator(val)
                
              }}
              setView = {setView}
            />
          </div>
          </div>)}
      <div>
        {inCreator && (
          <GroupCreator
            setInCreator={(val) => {
              setInCreator(val)
            }}
            setView = {setView}
          />
        )}
    </div>
      </>
  )
}