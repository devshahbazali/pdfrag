from pdfrag.config import settings
DEFGAULT_SAPARATERS=["\n\n","\n", ". ", "! ", "? ", "; ", ", ", " ", ""]

def _recursive_splitter(text:str,saparators:list[str],chunk_size:int)->list[str]:
    #if the text size good then return the text
    
    if len(text)<=chunk_size:
        return [text]

    #if no saparetors are available just devide the part of lenght chunksize
    if not saparators:
        return [text[i:i+chunk_size]  for i in range(0,len(text),chunk_size) ]

    sep, *rest= saparators

    parts=text.split(sep)
    # Re-attach the separator to each part end e.g.(".")(except the last) so we don't lose it
    pieces = [p + sep for p in parts[:-1]] + [parts[-1]]
    chunks: list[str] = []
    buffer = ""

    for piece in pieces:

        # Step 1: Check if the new piece fits in the current buffer
        if len(buffer) + len(piece) <= chunk_size:
            # If it fits, add it to the buffer
            buffer += piece

        else:
            # Step 2: The new piece does not fit.
            # Save the current buffer as a completed chunk.
            if buffer:
                chunks.append(buffer)

            # Step 3: Check if the new piece is too big by itself
            if len(piece) > chunk_size:

                # If it is too big, split it into smaller chunks
                # Add all the smaller chunks to the chunks list
                chunks.extend(_recursive_splitter(
                    piece, rest, chunk_size
                ))

                # Clear the buffer because the piece was already processed
                buffer = ""

            else:
                # Step 4: The piece fits by itself.
                # Start a new buffer with this piece.
                buffer = piece

    # Step 5: Save any remaining text in the buffer when The piece fits by itself and loop overs.
    if buffer:
        chunks.append(buffer)
    return chunks
def splitter(text:str,
             chunk_size:int|None=None,
             chunk_overlap:int |None=None) -> list[str]:

    chunk_size=chunk_size or settings.CHUNK_SIZE
    chunk_overlap= chunk_overlap or settings.CHUNK_OVERLAP

   

    raw_chunks=_recursive_splitter(text,DEFGAULT_SAPARATERS,chunk_size)
        #removing the white spaces from chunks
    raw_chunks=[c.strip() for c in raw_chunks if c.strip()]

    if chunk_overlap<=0 or len(raw_chunks)<=0:
        return raw_chunks
    
    #first chunk dont need to be overlapped by previous
    overlapped_chunks:list[str]= [raw_chunks[0]]

    for i in range(1,len(raw_chunks)):
        tail_of_prev_chunk=raw_chunks[i-1][-chunk_overlap:]
        overlapped_chunks.append(tail_of_prev_chunk+raw_chunks[i])
    
    return overlapped_chunks
