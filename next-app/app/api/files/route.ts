import { NextResponse } from 'next/server';
import { FileData } from '@/lib/types';

const MOCK_FILES: FileData[] = [
    { id: 1, name: 'research_paper.pdf', size: '2.3 MB', user: 'test@example.com', 'date': '2024-01-15' },
    { id: 2, name: 'data_analysis.csv', size: '1.1 MB', user: 'test@example.com', 'date': '2024-01-20' },
    { id: 3, name: 'presentation.pptx', size: '5.2 MB', user: 'test@example.com', 'date': '2024-02-01' },
    { id: 4, name: 'project_proposal.docx', size: '1.8 MB', user: 'manager@example.com', 'date': '2024-02-05' },
];

export async function GET() {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return NextResponse.json(MOCK_FILES);
}
