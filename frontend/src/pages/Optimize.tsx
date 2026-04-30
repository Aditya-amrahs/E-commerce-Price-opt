import { useState } from "react";
import Card from "../components/Card";
import { apiUrl } from "../lib/api";

const Optimize = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runOptimization = async () => {
    try {
      setLoading(true);

      const res = await fetch(apiUrl("/optimize"));
      const result = await res.json();

      setData(result);
    } catch (err) {
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <Card title="Model Optimization">
        <button
          onClick={runOptimization}
          className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 mb-4 rounded"
        >
          Run Optimization
        </button>

        {loading && <p className="text-gray-600">Running optimization...</p>}

        {data && (
          <div className="space-y-2 text-sm">
            <p><b>MSE:</b> {data.mse}</p>
            <p><b>RMSE:</b> {data.rmse}</p>
            <p><b>R² Score:</b> {data.r2}</p>
            <p><b>Average Price:</b> ₹{data.avg_price}</p>
            <p><b>Error %:</b> {data.error_percent}%</p>

            <p>
              <b>Model Quality:</b>{" "}
              <span
                className={
                  data.model_quality === "excellent"
                    ? "text-green-600 font-semibold"
                    : data.model_quality === "good"
                    ? "text-blue-600 font-semibold"
                    : data.model_quality === "acceptable"
                    ? "text-yellow-600 font-semibold"
                    : "text-red-600 font-semibold"
                }
              >
                {data.model_quality}
              </span>
            </p>

            <p><b>Sample Size:</b> {data.sample_size}</p>

          </div>
        )}
      </Card>
    </div>
  );
};

export default Optimize;
