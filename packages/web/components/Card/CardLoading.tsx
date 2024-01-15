const CardLoading = () => {
  return (
    <div className="border-blue-300 mx-auto w-full max-w-lg cursor-wait rounded-md border p-4 shadow">
      <div className="flex animate-pulse space-x-4">
        <div className="h-10 w-10 rounded-full bg-gray-300"></div>
        <div className="flex-1 space-y-6 py-1">
          <div className="h-2 rounded bg-gray-300"></div>
          <div className="space-y-7">
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-2 h-2 rounded bg-gray-300"></div>
              <div className="col-span-1 h-2 rounded bg-gray-300"></div>
            </div>
            <div className="h-2 rounded bg-gray-300"></div>
            <div className="h-2 rounded bg-gray-300"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CardLoading;
