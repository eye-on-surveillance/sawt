"use client";
import { HOME_PATH } from "@/lib/paths";
// Copied from: https://medium.com/@ryaddev/creating-a-responsive-navbar-with-react-and-tailwind-css-502cceaf9f53
import { faBars, faClose } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import SAWTLogo from "../../public/photos/Sawt.png";
import styles from "./navbar.module.scss";

export const navLinks = [
  {
    id: "about",
    title: "About",
  },
  {
    id: "tips",
    title: "How to use",
  },
  {
    id: "feedback",
    title: "Feedback",
  },
];

const Navbar = () => {
  const [active, setActive] = useState("Home");
  const [toggle, setToggle] = useState(false);

  return (
    <div className={styles["nav"]}>
      <div className="text-center md:flex">
        <div className="md:grow"></div>
        <div className="md:w-3/4 md:max-w-2xl">
          <nav className="navbar flex w-full items-center justify-between">
            <Link href={HOME_PATH}>
              <Image src={SAWTLogo} alt="SAWT Logo" width={100} height={100} />
              <div className={styles["beta"]}>
                <p>beta</p>
              </div>
            </Link>
            {/* Desktop Navigation */}
            <ul className="hidden flex-1 list-none items-center justify-end sm:flex">
              {navLinks.map((nav, index) => (
                <li
                  key={nav.id}
                  className={`font-poppins font-regular cursor-pointer text-[16px] ${
                    active === nav.title ? "text-white" : "text-dimWhite"
                  } ${index === navLinks.length - 1 ? "mr-0" : "mr-10"}`}
                  onClick={() => setActive(nav.title)}
                >
                  <a href={`/${nav.id}`}>{nav.title}</a>
                </li>
              ))}
            </ul>

            {/* Mobile Navigation */}
            <div className="flex flex-1 items-center justify-end sm:hidden">
              {/* https://github.com/FortAwesome/Font-Awesome/tree/6.x/js-packages/%40fortawesome/free-solid-svg-icons */}
              <FontAwesomeIcon
                className="h-[28px] w-[28px] cursor-pointer object-contain"
                icon={toggle ? faClose : faBars}
                onClick={() => setToggle(!toggle)}
              />

              {/* Sidebar */}
              <div
                className={`${
                  !toggle ? "hidden" : "flex"
                } sidebar absolute right-0 top-20 mx-4 my-2 min-w-[140px] rounded-xl bg-primary p-6 text-white`}
              >
                <ul className="flex flex-1 list-none flex-col items-start justify-end">
                  {navLinks.map((nav, index) => (
                    <li
                      key={nav.id}
                      className={`font-poppins cursor-pointer text-[16px] font-medium ${
                        active === nav.title ? "text-white" : "text-dimWhite"
                      } ${index === navLinks.length - 1 ? "mb-0" : "mb-4"}`}
                      onClick={() => setActive(nav.title)}
                    >
                      <Link href={`/${nav.id}`}>{nav.title}</Link>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </nav>
        </div>
        <div className="md:grow"></div>
      </div>
    </div>
  );
};

export default Navbar;
