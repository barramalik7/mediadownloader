import { createFileRoute } from '@tanstack/react-router'
import { DownloaderForm } from '@/components/features/DownloaderForm'

export const Route = createFileRoute('/')({
    component: Index,
})

function Index() {
    return (
        <div className="p-2 container mx-auto max-w-4xl py-10">
            <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-6 text-center">
                Download Context
            </h1>
            <p className="text-xl text-muted-foreground text-center mb-10">
                Download videos and media from your favorite platforms.
            </p>

            <div className="py-6">
                <DownloaderForm />
            </div>
        </div>
    )
}
