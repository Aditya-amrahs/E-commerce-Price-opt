import { useState } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import Analysis from "./pages/Analysis";
import Predict from "./pages/Predict";
import Optimize from "./pages/Optimize";
import Summary from "./pages/Summary";
import Adjust from "./pages/Adjust";
function App() {
  const [page, setPage] = useState("Dashboard");

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
      case "Adjust":
        return <Adjust />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div>
      <Navbar setPage={setPage} />
      {renderPage()}
    </div>
  );
}

export default App;