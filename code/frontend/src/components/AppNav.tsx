import { NavLink } from "react-router";

import libraryIconDark from "../assets/icons/nav/library-icon-dark.svg";
import libraryIconLight from "../assets/icons/nav/library-icon-light.svg";
import analysisIconDark from "../assets/icons/nav/analysis-icon-dark.svg";
import analysisIconLight from "../assets/icons/nav/analysis-icon-light.svg";

function AppNav() {
  return (
    <nav className="h-full flex-initial  border-r-2 border-r-gray-200 p-2">
      <NavLink className="m-4 flex items-center justify-center" to={"/"}>
        <div className="h-12">
          <img className="h-full" src="/danceable-logo.svg" alt="danceable logo" />
        </div>
      </NavLink>
      <NavLink
        className={({ isActive }) =>
          `m-2 flex aspect-square items-center justify-center rounded-2xl p-4 transition
          ${isActive ? "bg-gray-dark" : "bg-gray-100 hover:bg-gray-200"}`
        }
        to={"/library"}
      >
        {({ isActive }) => (
          <div className="w-6">
            <img
              className="w-full"
              src={isActive ? libraryIconLight : libraryIconDark}
              alt="library nav link"
            />
          </div>
        )}
      </NavLink>
      <NavLink
        className={({ isActive }) =>
          `m-2 flex aspect-square items-center justify-center rounded-2xl p-4 transition
          ${isActive ? "bg-gray-dark" : "bg-gray-100 hover:bg-gray-200"}`
        }
        to={"/analysis"}
      >
        {({ isActive }) => (
          <div className="w-6">
            <img
              className="w-full"
              src={isActive ? analysisIconLight : analysisIconDark}
              alt="library nav link"
            />
          </div>
        )}
      </NavLink>
    </nav>
  );
}

export default AppNav;
