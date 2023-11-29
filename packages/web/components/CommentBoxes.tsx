import { ICard } from "@/lib/api";
import { faComment } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";

interface CommentBoxProps {
    card: ICard;
    onSubmit: ( data: { comment: string, card: ICard }) => void;
}

export default function CommentBox({ onSubmit, card }: CommentBoxProps) {
    const [comment, setComment] = useState<string>("");
    const handleSubmit = () => {
        onSubmit( { comment , card});
        setComment("");
    };


    return (
        <div className="my-12">
        <div className="relative  block">
        <label htmlFor="comment" className="mb-2 mt-4 block">
        <FontAwesomeIcon
            className="left-2 top-1/2 ml-2 h-[20px] w-[28px] cursor-pointer object-contain"
            icon={faComment}
        />
        Comments:
        </label>
        <textarea
            id="comment"
            className="h-20 w-full rounded border p-2"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add feedback here"
        ></textarea>
        </div>
        <button
        onClick={handleSubmit}
        className="bg-blue-500 rounded bg-secondary px-4 py-2 text-white"
        >
        Submit
        </button>
    </div>
    );
}