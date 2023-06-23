import { RESPONSE_TYPE_DEPTH, RESPONSE_TYPE_GENERAL } from "@/lib/api";
import { RadioGroup } from "@headlessui/react";
import React from "react";

interface ResponseToggleProps {
  onToggle: (selected: string) => void;
}

function ResponseToggle({ onToggle }: ResponseToggleProps) {
  // eslint-disable-next-line unused-imports/no-unused-vars
  let [selected, setSelected] = React.useState(RESPONSE_TYPE_GENERAL);

  React.useEffect(() => {
    onToggle(selected);
  }, [selected, onToggle]);

  return (
    <div>
      <RadioGroup value={selected} onChange={setSelected}>
        <RadioGroup.Option value={RESPONSE_TYPE_GENERAL}>
          {({ checked }) => (
            <>
              <span
                className={` ${
                  checked ? "bg-blue-900 text-white" : "bg-white text-black"
                } inline-flex items-center rounded-full px-4 py-2 text-sm font-medium capitalize cursor-pointer`}
              >
                General Summary
              </span>
            </>
          )}
        </RadioGroup.Option>
        <RadioGroup.Option value={RESPONSE_TYPE_DEPTH}>
          {({ checked }) => (
            <>
              <span
                className={` ${
                  checked ? "bg-blue-900 text-white" : "bg-white text-black"
                } inline-flex items-center rounded-full px-4 py-2 text-sm font-medium capitalize cursor-pointer`}
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
