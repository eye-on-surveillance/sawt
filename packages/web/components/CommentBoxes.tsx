
import { ICard } from "@/lib/api";
import { faComment } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";

interface CommentBoxProps {
    scores: Record<string, number>
    card: ICard;
    onSubmit: (data: { comment: string, card: ICard, scores: Record<string, number> }) => void;
    onReset: () => void;  
}

export default function CommentBox({ onSubmit, card, scores, onReset }: CommentBoxProps) {
    const [comment, setComment] = useState<string>("");
    // const [scores, setRubricScores] = useState<Record<string, number>>({});

    const handleSubmit = () => {
        onSubmit({ comment, card, scores});
        setComment("");
        onReset();  // Reset the scores after submission
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
            className="h-32 w-full rounded border p-2"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Add feedback here"
        ></textarea>
        </div>
        <div className="flex justify-center mt-4">
            <button
                onClick={handleSubmit}
                className="bg-blue-500 rounded bg-secondary px-4 py-2 text-white"
            >
                Submit
            </button>
        </div>
    </div>
    );
}