import { useState } from "react";
import Card from "../components/Card";

const Predict = () => {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<any>(null);

  const handleSubmit = () => {
    fetch("http://127.0.0.1:8000/optimize") // fallback using optimize
      .then((res) => res.json())
      .then((res) => setResult(res));
  };

  return (
    <div className="p-6">
      <Card title="Predict Price">
        <input
          placeholder="Enter any value (demo)"
          className="border p-2 mr-2"
          onChange={(e) => setInput(e.target.value)}
        />

        <button
          onClick={handleSubmit}
          className="bg-blue-500 text-white px-3 py-1"
        >
          Predict
        </button>

        {result && (
          <div className="mt-3">
            <p>Predicted (via model): {result.optimized_mse}</p>
          </div>
        )}
      </Card>
    </div>
  );
};

export default Predict;