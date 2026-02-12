import { useState } from "react"
import { Loader2, Download, AlertCircle, CheckCircle2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"

export function DownloaderForm() {
    const [url, setUrl] = useState("")
    const [quality, setQuality] = useState("1")
    const [format, setFormat] = useState<"mp4" | "mp3" | "jpg" | "png">("mp4")

    // Download State
    const [isDownloading, setIsDownloading] = useState(false)
    const [progress, setProgress] = useState(0)
    const [statusMessage, setStatusMessage] = useState("")
    const [error, setError] = useState<string | null>(null)
    const [isSuccess, setIsSuccess] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!url) return

        setIsDownloading(true)
        setProgress(0)
        setStatusMessage("Starting download...")
        setError(null)
        setIsSuccess(false)

        try {
            const response = await fetch("/api/download/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ url, quality, format }),
            })

            if (!response.ok) {
                // If API returns 4xx/5xx immediately (not a stream)
                const errorData = await response.json()
                throw new Error(errorData.detail || "Failed to start download")
            }

            if (!response.body) throw new Error("No response body")

            const reader = response.body.getReader()
            const decoder = new TextDecoder()
            let buffer = ""

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                const chunk = decoder.decode(value, { stream: true })
                buffer += chunk

                // Process incomplete chunks
                const lines = buffer.split("\n\n")
                buffer = lines.pop() || "" // Keep the last incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const jsonStr = line.slice(6)
                        try {
                            const data = JSON.parse(jsonStr)

                            if (data.status === "downloading") {
                                if (data.progress) setProgress(data.progress)
                                if (data.log) setStatusMessage(data.log) // Optional: show raw logs
                            } else if (data.status === "completed") {
                                setProgress(100)
                                setIsSuccess(true)
                                setStatusMessage(data.message)
                            } else if (data.status === "error") {
                                throw new Error(data.message)
                            }
                        } catch (e) {
                            console.error("Failed to parse SSE data", e)
                        }
                    }
                }
            }

        } catch (err) {
            setError(err instanceof Error ? err.message : "An unknown error occurred")
            setStatusMessage("Download failed")
        } finally {
            setIsDownloading(false)
        }
    }

    return (
        <Card className="w-full max-w-xl mx-auto border-border bg-card/50 backdrop-blur-sm">
            <CardHeader>
                <CardTitle>Download Media</CardTitle>
                <CardDescription>
                    Supports YouTube, TikTok, Instagram, Twitter, Pinterest, and Spotify.
                </CardDescription>
            </CardHeader>
            <form onSubmit={handleSubmit}>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="url">Media URL</Label>
                        <Input
                            id="url"
                            placeholder="Paste your link here..."
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            disabled={isDownloading}
                            required
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="quality">Quality</Label>
                            <Select value={quality} onValueChange={setQuality} disabled={isDownloading}>
                                <SelectTrigger id="quality">
                                    <SelectValue placeholder="Select quality" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="1">Best Available</SelectItem>
                                    <SelectItem value="2">1080p</SelectItem>
                                    <SelectItem value="3">720p</SelectItem>
                                    <SelectItem value="4">480p</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="format">Format</Label>
                            <Select value={format} onValueChange={(v: "mp4" | "mp3" | "jpg" | "png") => setFormat(v)} disabled={isDownloading}>
                                <SelectTrigger id="format">
                                    <SelectValue placeholder="Select format" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="mp4">Video (MP4)</SelectItem>
                                    <SelectItem value="mp3">Audio (MP3)</SelectItem>
                                    <SelectItem value="jpg">Photo (JPG)</SelectItem>
                                    <SelectItem value="png">Photo (PNG)</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {isDownloading && (
                        <div className="space-y-2">
                            <div className="flex justify-between text-xs text-muted-foreground">
                                <span>{statusMessage}</span>
                                <span>{Math.round(progress)}%</span>
                            </div>
                            <Progress value={progress} className="w-full" />
                        </div>
                    )}

                    {error && (
                        <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm flex items-center gap-2">
                            <AlertCircle className="h-4 w-4" />
                            <span>{error}</span>
                        </div>
                    )}

                    {isSuccess && (
                        <div className="p-3 rounded-md bg-green-500/10 text-green-600 dark:text-green-500 text-sm flex items-center gap-2">
                            <CheckCircle2 className="h-4 w-4" />
                            <span>Download completed successfully!</span>
                        </div>
                    )}

                </CardContent>
                <CardFooter>
                    <Button type="submit" className="w-full" disabled={isDownloading || !url}>
                        {isDownloading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Downloading...
                            </>
                        ) : (
                            <>
                                <Download className="mr-2 h-4 w-4" />
                                Start Download
                            </>
                        )}
                    </Button>
                </CardFooter>
            </form>
        </Card>
    )
}

