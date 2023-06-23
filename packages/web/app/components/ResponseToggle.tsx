"use client";
import { RadioGroup } from "@headlessui/react";
import React from "react";

function ResponseToggle({ onToggle }) {
  let [selected, setSelected] = React.useState("General Summary");

  React.useEffect(() => {
    onToggle(selected);
  }, [selected, onToggle]);

  return (
    <div>
      <RadioGroup value={selected} onChange={setSelected}>
        <RadioGroup.Option value="General Summary">
          {({ checked }) => (
            <>
              <span
                className={` ${
                  checked ? "bg-blue-900 text-white" : "bg-white text-black"
                } inline-flex items-center rounded-full px-4 py-2 text-sm font-medium capitalize`}
              >
                General Summary
              </span>
            </>
          )}
        </RadioGroup.Option>
        <RadioGroup.Option value="In-Depth Report">
          {({ checked }) => (
            <>
              <span
                className={` ${
                  checked ? "bg-blue-900 text-white" : "bg-white text-black"
                } inline-flex items-center rounded-full px-4 py-2 text-sm font-medium capitalize`}
              >
                In-Depth Report
              </span>
            </>
          )}
        </RadioGroup.Option>
      </RadioGroup>
    </div>
  );
}

export default ResponseToggle;
