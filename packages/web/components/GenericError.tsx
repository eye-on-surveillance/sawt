"use client";

import Link from "next/link";

export default function GenericError() {
  return (
    <div className="flex min-h-[97vh] flex-col justify-center justify-items-center bg-broken-camera bg-cover ">
      <div className="m-auto flex w-2/3 flex-col justify-center justify-items-center space-y-4 rounded-lg py-12 text-center font-serif backdrop-brightness-50 lg:w-1/3">
        <div>
          <p className="text-4xl text-white">Oh snap, it broke!</p>
        </div>
        <div>
          <Link href="/">
            <span className="text-2xl text-secondary brightness-100">
              Return home
            </span>
          </Link>
        </div>
      </div>
    </div>
  );
}
