import { APP_NAME } from "@/lib/copy";
import { faCamera } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import Link from "next/link";

export default function Footer() {
  return (
    <div className="py-12 text-center text-white">
      <p>
        <Link href="https://eyeonsurveillance.org" target="_blank">
          Without
          <FontAwesomeIcon
            icon={faCamera}
            className="mx-2 h-7 w-7 align-middle"
          />
          by EOS
        </Link>
      </p>
      <p className="mt-3">
        &copy; {new Date().getFullYear()} {APP_NAME}
      </p>
    </div>
  );
}
