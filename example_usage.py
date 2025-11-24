"""
Example usage of the Batch File Retrieval System
"""
from bot.api import BatchFileAPI
from bot.utils import format_file_size
import json


def main():
    """
    Demonstrate the batch file retrieval system
    """
    # Initialize API
    api = BatchFileAPI()
    
    # Example 1: Get all batches for an organization
    print("=" * 60)
    print("Example 1: Retrieve all batches for an org code")
    print("=" * 60)
    
    org_code = "ABC123"
    result = api.get_batches_by_org_code(org_code)
    
    if result['success']:
        print(f"\n✓ Found {result['batch_count']} batches for {result['org_name']}")
        print(f"\nBatch List:")
        for batch in result['batches']:
            print(f"  - {batch['batch_name']}")
            print(f"    ID: {batch['batch_id']}")
            print(f"    File: {batch['filename']}")
            print(f"    Size: {batch['file_size_formatted']}")
            print(f"    Downloaded: {'Yes' if batch['downloaded'] else 'No'}")
            print()
    else:
        print(f"\n✗ Error: {result['message']}")
    
    # Example 2: Download a specific batch file
    print("\n" + "=" * 60)
    print("Example 2: Download a specific batch file")
    print("=" * 60)
    
    if result['success'] and result['batches']:
        batch_id = result['batches'][0]['batch_id']
        
        download_result = api.download_batch(batch_id, org_code)
        
        if download_result['success']:
            print(f"\n✓ Downloaded: {download_result['filename']}")
            print(f"  Size: {download_result['file_size_formatted']}")
            print(f"  Type: {download_result['content_type']}")
            
            # Save file to disk
            output_path = f"downloads/{download_result['filename']}"
            with open(output_path, 'wb') as f:
                f.write(download_result['file_data'])
            print(f"  Saved to: {output_path}")
        else:
            print(f"\n✗ Download failed: {download_result['message']}")
    
    # Example 3: Sync all batches for an organization
    print("\n" + "=" * 60)
    print("Example 3: Sync all batches (download all files)")
    print("=" * 60)
    
    sync_result = api.sync_org_batches(org_code, force_refresh=False)
    
    if sync_result['success']:
        print(f"\n✓ Sync completed successfully")
        print(f"  Total files: {sync_result['total_files']}")
        print(f"  Downloaded: {sync_result['downloaded_files']}")
        print(f"  Failed: {sync_result['failed_files']}")
        print(f"  Total size: {sync_result['total_bytes_formatted']}")
        print(f"  Duration: {sync_result['duration_seconds']:.2f} seconds")
        print(f"  Progress: {sync_result['progress_percentage']:.1f}%")
    else:
        print(f"\n✗ Sync failed: {sync_result['message']}")
    
    # Example 4: Get information about a specific batch
    print("\n" + "=" * 60)
    print("Example 4: Get batch file information")
    print("=" * 60)
    
    if result['success'] and result['batches']:
        batch_id = result['batches'][0]['batch_id']
        
        info_result = api.get_batch_info(batch_id)
        
        if info_result['success']:
            batch = info_result['batch']
            print(f"\n✓ Batch Information:")
            print(f"  ID: {batch['batch_id']}")
            print(f"  Name: {batch['batch_name']}")
            print(f"  Org Code: {batch['org_code']}")
            print(f"  Filename: {batch['filename']}")
            print(f"  Size: {batch['file_size_formatted']}")
            print(f"  Type: {batch['content_type']}")
            print(f"  Created: {batch['created_at']}")
            print(f"  Downloaded: {'Yes' if batch['downloaded'] else 'No'}")
            if batch['downloaded']:
                print(f"  Downloaded at: {batch['downloaded_at']}")
        else:
            print(f"\n✗ Error: {info_result['message']}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Create downloads directory
    import os
    os.makedirs("downloads", exist_ok=True)
    
    # Run examples
    main()
