import { APP_NAME } from "@/lib/copy";
import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

export default function NewQuery() {
  return (
    <div className="my-12">
      <div className="relative  block">
        <FontAwesomeIcon
          className="align-center absolute left-2 top-1/2 ml-2 h-[28px] w-[28px] -translate-y-1/2 transform cursor-pointer object-contain"
          icon={faMagnifyingGlass}
        />
        <input
          className="focus:shadow-outline mb-3 block w-full appearance-none rounded-lg px-16 py-2 leading-tight text-gray-700 shadow focus:outline-none"
          id="new-query"
          type="text"
          placeholder={`Ask ${APP_NAME}`}
        ></input>
        {/* <p className="text-xs italic text-red-500">Please choose a password.</p> */}
      </div>
      <button className="btn w-full rounded-lg bg-blue-600 p-2 text-2xl text-white">
        Get answer
      </button>
    </div>
  );
}
