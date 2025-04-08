import { Outlet } from "react-router";
import AppNav from "./AppNav";

const RootLayout = () => {
  return (
    <div className="flex h-screen">
      <AppNav />

      <main className="flex-auto">
        <Outlet />
      </main>
    </div>
  );
};

export default RootLayout;
