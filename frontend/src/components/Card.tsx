type Props = {
  title: string;
  children: React.ReactNode;
};

const Card = ({ title, children }: Props) => {
  return (
    <div className="bg-white p-4 rounded-xl shadow-md">
      <h2 className="font-semibold text-lg mb-3">{title}</h2>
      {children}
    </div>
  );
};

export default Card;