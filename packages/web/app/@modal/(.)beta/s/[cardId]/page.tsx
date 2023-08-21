import Modal from "@/components/Modal";
import ClientCard from "./ClientCard";

export default async function CardModal({
  params,
}: {
  params: { cardId: string };
}) {
  const { cardId } = params;

  return (
    <Modal>
      <div className="bg-slate-500 md:max-w-5xl">
        <ClientCard cardId={cardId} />
      </div>
    </Modal>
  );
}
