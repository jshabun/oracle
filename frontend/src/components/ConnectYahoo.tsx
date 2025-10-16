"use client";
import { Button } from "@heroui/react";
import { getAuthUrl } from "@/lib/api";

export default function ConnectYahoo() {
  const onConnect = async () => {
    const url = await getAuthUrl();
    window.location.href = url;
  };
  return (
    <Button onPress={onConnect} radius="lg" size="lg">Connect Yahoo</Button>
  );
}