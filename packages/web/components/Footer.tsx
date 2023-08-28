import { APP_NAME } from "@/lib/copy";
import {
  faGithub,
  faInstagram,
  faTwitter,
} from "@fortawesome/free-brands-svg-icons";
import { faCamera } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import Link from "next/link";

export default function Footer() {
  return (
    <div className="py-12 text-center text-blue">
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
      <p className="my-5">
        <Link
          href="https://github.com/eye-on-surveillance/sawt"
          target="_blank"
        >
          <FontAwesomeIcon
            icon={faGithub}
            className="mx-2 h-7 w-7 align-middle"
          />
        </Link>
        <Link href="https://instagram.com/eos_nola" target="_blank">
          <FontAwesomeIcon
            icon={faInstagram}
            className="mx-2 h-7 w-7 align-middle"
          />
        </Link>
        <Link href="https://twitter.com/eos_nola" target="_blank">
          <FontAwesomeIcon
            icon={faTwitter}
            className="mx-2 h-7 w-7 align-middle"
          />
        </Link>
      </p>

      <p>
        &copy; {new Date().getFullYear()} {APP_NAME}
      </p>
    </div>
  );
}
