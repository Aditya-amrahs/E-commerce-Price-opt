import { useEffect, useState } from "react";
import Card from "../components/Card";
import PriceChart from "../components/PriceChart";

const Summary = () => {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/analysis")
      .then((res) => res.json())
      .then(setData);
  }, []);

  return (
    <div className="p-6">
      <Card title="Data Summary">
        <PriceChart data={data} />
      </Card>
    </div>
  );
};

export default Summary;