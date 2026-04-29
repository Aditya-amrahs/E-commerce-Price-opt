import { useState } from "react";
import Navbar from "./src/components/Navbar";
import Dashboard from "./src/pages/Dashboard";
import Analysis from "./src/pages/Analysis";
import Predict from "./src/pages/Predict";
import Optimize from "./src/pages/Optimize";
import Summary from "./src/pages/Summary";

// Strong typing
type Page =
  | "Dashboard"
  | "Analysis"
  | "Predict"
  | "Optimize"
  | "Summary";

function App() {
  const [page, setPage] = useState<Page>("Dashboard");

  const renderPage = () => {
    switch (page) {
      case "Analysis":
        return <Analysis />;
      case "Predict":
        return <Predict />;
      case "Optimize":
        return <Optimize />;
      case "Summary":
        return <Summary />;
      case "Dashboard":
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navbar */}
      <Navbar setPage={setPage} />

      {/* Page Content */}
      <div className="max-w-7xl mx-auto">
        {renderPage()}
      </div>
    </div>
  );
}

export default App;