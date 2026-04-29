import { useState } from "react";

const tabs = ["Dashboard", "Analysis", "Predict", "Optimize", "Summary","Adjust"];

const Navbar = ({ setPage }: any) => {
  const [active, setActive] = useState("Dashboard");

  return (
    <div className="flex flex-wrap gap-3 p-4 bg-gray-900 text-white shadow">
      {tabs.map((tab) => (
        <button
          key={tab}
          onClick={() => {
            setActive(tab);
            setPage(tab);
          }}
          className={`px-4 py-1 rounded-lg transition ${
            active === tab
              ? "bg-blue-500"
              : "bg-gray-700 hover:bg-gray-600"
          }`}
        >
          {tab}
        </button>
      ))}
    </div>
  );
};

export default Navbar;