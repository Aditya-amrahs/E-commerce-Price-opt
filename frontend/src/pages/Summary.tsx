import { useEffect, useState } from "react";
import Card from "../components/Card";

const Summary = () => {
  const [data, setData] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/analysis")
      .then((res) => res.json())
      .then((res) => {
        setData(res.data || []);
        setSummary(res.summary || null);
      });
  }, []);

  // ✅ Compute insights from sample
  const total = data.length;

  const higher = data.filter((d) => d.status === "Higher").length;
  const lower = data.filter((d) => d.status === "Lower").length;
  const equal = data.filter((d) => d.status === "Equal").length;

  const higherPercent = total ? ((higher / total) * 100).toFixed(1) : 0;
  const lowerPercent = total ? ((lower / total) * 100).toFixed(1) : 0;

  return (
    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">

      {/* Dataset Summary */}
      <Card title="Dataset Overview">
        <p>Total Products: {summary?.total_products?.toLocaleString()}</p>
        <p>Average Price: ₹{summary?.avg_price?.toFixed(2)}</p>
        <p>Min Price: ₹{summary?.min_price?.toFixed(2)}</p>
        <p>Max Price: ₹{summary?.max_price?.toFixed(2)}</p>
      </Card>

      {/* Pricing Insights */}
      <Card title="Pricing Insights">
        <p>Overpriced Products: {higher} ({higherPercent}%)</p>
        <p>Underpriced Products: {lower} ({lowerPercent}%)</p>
        <p>Correctly Priced: {equal}</p>
      </Card>

      {/* Recommendations */}
      <Card title="Recommendations">
        <p>Reduce prices for overpriced products</p>
        <p>Increase prices for underpriced products</p>
        <p>Maintain prices where competitive</p>
      </Card>

      {/* Model Insight */}
      <Card title="Model Insight">
        <p>
          The system analyzes competitor pricing trends and recommends optimal
          pricing strategies to maximize competitiveness and profitability.
        </p>
      </Card>

    </div>
  );
};

export default Summary;