"use client";

import GenericError from "@/components/GenericError";

export default function Error({}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <GenericError />;
}
