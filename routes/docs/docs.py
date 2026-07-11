from flask import Blueprint, render_template_string

docsbp = Blueprint("docs", __name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PersonalDrive API Playground</title>
    <!-- Outfit Font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-color: #0f111a;
            --sidebar-bg: #141724;
            --card-bg: #1a1d30;
            --text-color: #e2e8f0;
            --text-muted: #8892b0;
            --primary: #8a2be2;
            --primary-glow: rgba(138, 43, 226, 0.4);
            --border-color: #2a2e45;
            
            /* Method Colors */
            --get-color: #00bcd4;
            --post-color: #4caf50;
            --put-color: #ff9800;
            --delete-color: #f44336;
            
            --get-bg: rgba(0, 188, 212, 0.1);
            --post-bg: rgba(76, 175, 80, 0.1);
            --put-bg: rgba(255, 152, 0, 0.1);
            --delete-bg: rgba(244, 67, 54, 0.1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.5;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* Sidebar Styling */
        .sidebar {
            width: 320px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            height: 100%;
            flex-shrink: 0;
        }

        .sidebar-header {
            padding: 24px;
            border-bottom: 1px solid var(--border-color);
        }

        .sidebar-header h1 {
            font-size: 22px;
            font-weight: 700;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .sidebar-header h1 span {
            font-size: 12px;
            background: linear-gradient(135deg, #a855f7, #6366f1);
            padding: 2px 8px;
            border-radius: 20px;
            font-weight: 600;
        }

        .search-container {
            padding: 16px 24px;
            border-bottom: 1px solid var(--border-color);
        }

        .search-input {
            width: 100%;
            padding: 10px 16px;
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-color);
            font-family: inherit;
            outline: none;
            transition: all 0.3s;
        }

        .search-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 8px var(--primary-glow);
        }

        .endpoint-list {
            flex: 1;
            overflow-y: auto;
            padding: 16px 0;
        }

        .category-group {
            margin-bottom: 24px;
        }

        .category-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-muted);
            padding: 0 24px 8px 24px;
            font-weight: 700;
        }

        .endpoint-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 24px;
            cursor: pointer;
            transition: background-color 0.2s;
            font-size: 14px;
        }

        .endpoint-item:hover {
            background-color: rgba(255, 255, 255, 0.05);
        }

        .endpoint-item.active {
            background-color: rgba(138, 43, 226, 0.15);
            border-left: 3px solid var(--primary);
        }

        .method-badge {
            font-size: 10px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            width: 60px;
            text-align: center;
            flex-shrink: 0;
            letter-spacing: 0.5px;
        }

        .method-badge.get { color: var(--get-color); background-color: var(--get-bg); border: 1px solid rgba(0, 188, 212, 0.3); }
        .method-badge.post { color: var(--post-color); background-color: var(--post-bg); border: 1px solid rgba(76, 175, 80, 0.3); }
        .method-badge.put { color: var(--put-color); background-color: var(--put-bg); border: 1px solid rgba(255, 152, 0, 0.3); }
        .method-badge.delete { color: var(--delete-color); background-color: var(--delete-bg); border: 1px solid rgba(244, 67, 54, 0.3); }

        .endpoint-name {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: #d1d5db;
        }

        /* Main Workspace Container */
        .workspace {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            background-color: var(--bg-color);
        }

        /* Top Configuration Panel */
        .top-config {
            background-color: var(--sidebar-bg);
            border-bottom: 1px solid var(--border-color);
            padding: 16px 32px;
            display: flex;
            flex-wrap: wrap;
            gap: 24px;
            align-items: center;
            justify-content: space-between;
        }

        .config-inputs {
            display: flex;
            gap: 16px;
            flex-grow: 1;
            max-width: 900px;
        }

        .config-field {
            display: flex;
            flex-direction: column;
            gap: 6px;
            flex: 1;
        }

        .config-field label {
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
        }

        .config-field input {
            padding: 8px 12px;
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-color);
            font-family: inherit;
            font-size: 13px;
            outline: none;
            transition: border-color 0.3s;
        }

        .config-field input:focus {
            border-color: var(--primary);
        }

        /* Documentation Area */
        .doc-area {
            flex: 1;
            display: flex;
            overflow: hidden;
        }

        /* Endpoint Detail Panel */
        .detail-panel {
            flex: 1;
            padding: 32px;
            overflow-y: auto;
            border-right: 1px solid var(--border-color);
        }

        /* Right Response Panel */
        .response-panel {
            width: 45%;
            min-width: 400px;
            background-color: #0b0c16;
            padding: 32px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        /* Endpoint Card details */
        .endpoint-title-section {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }

        .endpoint-title-section h2 {
            font-size: 26px;
            font-weight: 700;
            color: #fff;
        }

        .full-path-container {
            display: flex;
            align-items: center;
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px 16px;
            font-family: 'Fira Code', monospace;
            font-size: 14px;
            margin-bottom: 24px;
            gap: 8px;
        }

        .full-path-url {
            color: #93c5fd;
            word-break: break-all;
        }

        .endpoint-desc {
            color: var(--text-muted);
            font-size: 15px;
            margin-bottom: 32px;
            background-color: rgba(138, 43, 226, 0.03);
            border-left: 4px solid var(--primary);
            padding: 16px;
            border-radius: 0 8px 8px 0;
        }

        /* Parameter Section */
        .section-header {
            font-size: 16px;
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
            margin-bottom: 16px;
            color: #fff;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .param-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
        }

        .param-table th, .param-table td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
            font-size: 14px;
        }

        .param-table th {
            color: var(--text-muted);
            font-weight: 500;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .param-name {
            font-family: 'Fira Code', monospace;
            font-weight: 600;
            color: #38bdf8;
        }

        .param-type {
            font-size: 11px;
            background-color: rgba(255, 255, 255, 0.05);
            padding: 2px 6px;
            border-radius: 4px;
            color: var(--text-muted);
        }

        .param-desc {
            color: var(--text-muted);
        }

        .param-input {
            width: 100%;
            padding: 8px 12px;
            background-color: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-color);
            font-family: inherit;
            outline: none;
        }

        .param-input:focus {
            border-color: var(--primary);
        }

        /* Body JSON Editor */
        .json-editor-container {
            position: relative;
            margin-bottom: 24px;
        }

        .json-editor {
            width: 100%;
            height: 200px;
            background-color: #0b0c16;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: #a78bfa;
            font-family: 'Fira Code', monospace;
            font-size: 13px;
            padding: 16px;
            outline: none;
            resize: vertical;
        }

        .json-editor:focus {
            border-color: var(--primary);
        }

        /* Send Button */
        .btn-send {
            background: linear-gradient(135deg, #8a2be2, #6366f1);
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 14px 28px;
            font-family: inherit;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            box-shadow: 0 4px 15px rgba(138, 43, 226, 0.4);
        }

        .btn-send:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(138, 43, 226, 0.6);
        }

        .btn-send:active {
            transform: translateY(0);
        }

        .btn-send:disabled {
            background: #4b5563;
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }

        /* Response Console Styles */
        .response-header-stats {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
        }

        .stat-badge {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
        }

        .stat-badge span {
            color: var(--text-muted);
            margin-right: 6px;
            font-weight: 400;
        }

        .status-success {
            color: #4caf50 !important;
            border-color: rgba(76, 175, 80, 0.3) !important;
            background-color: rgba(76, 175, 80, 0.05) !important;
        }

        .status-error {
            color: #f44336 !important;
            border-color: rgba(244, 67, 54, 0.3) !important;
            background-color: rgba(244, 67, 54, 0.05) !important;
        }

        .response-viewer {
            flex: 1;
            background-color: #05060b;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            font-family: 'Fira Code', monospace;
            font-size: 13px;
            overflow: auto;
            white-space: pre-wrap;
            color: #34d399;
        }

        .response-placeholder {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: var(--text-muted);
            gap: 16px;
            text-align: center;
        }

        .response-placeholder svg {
            width: 48px;
            height: 48px;
            stroke: var(--text-muted);
        }

        /* File Upload Multi UI */
        .file-upload-item {
            display: flex;
            flex-direction: column;
            gap: 8px;
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px dashed var(--border-color);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }

        /* Custom Scrollbars */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-color);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary);
        }

        /* Tooltip */
        .auth-badge {
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 500;
        }

        .auth-badge.public {
            background-color: rgba(16, 185, 129, 0.1);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }

        .auth-badge.private {
            background-color: rgba(245, 158, 11, 0.1);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }

        .badge-copy {
            cursor: pointer;
            transition: opacity 0.2s;
            margin-left: 8px;
        }

        .badge-copy:hover {
            opacity: 0.8;
        }
    </style>
</head>
<body>

    <!-- SIDEBAR -->
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>PersonalDrive <span>v1.0</span></h1>
        </div>
        <div class="search-container">
            <input type="text" id="search-bar" class="search-input" placeholder="Search endpoints...">
        </div>
        <div class="endpoint-list" id="endpoint-list-container">
            <!-- Dynamic groups will be injected here -->
        </div>
    </div>

    <!-- WORKSPACE -->
    <div class="workspace">
        <!-- Top Config Panel -->
        <div class="top-config">
            <div class="config-inputs">
                <div class="config-field">
                    <label for="global-token">Authorization (auth Header)</label>
                    <input type="text" id="global-token" placeholder="Paste JWT token here...">
                </div>
                <div class="config-field" style="max-width: 150px;">
                    <label for="global-userid">Global UserID</label>
                    <input type="number" id="global-userid" value="1" placeholder="User ID">
                </div>
                <div class="config-field">
                    <label for="global-base-url">Base URL</label>
                    <input type="text" id="global-base-url" placeholder="http://127.0.0.1:5002">
                </div>
            </div>
        </div>

        <!-- Documentation & Runner Area -->
        <div class="doc-area">
            <!-- Left detail column -->
            <div class="detail-panel" id="detail-panel">
                <!-- Dynamic endpoint details loaded here -->
            </div>

            <!-- Right console column -->
            <div class="response-panel" id="response-panel">
                <div class="section-header">Response Console</div>
                <div id="response-container-inner" class="response-placeholder">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p>Select an endpoint and click "Try it out" to see the API response here.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Endpoint Data and App Logic -->
    <script>
        const endpoints = [
            {
                category: "User Authentication",
                name: "Create User Account",
                method: "POST",
                path: "/createaccount/",
                isPublic: true,
                description: "Creates a new user account and returns a JWT token. Automatically logs in the user.",
                bodyType: "json",
                body: {
                    username: "example_user",
                    password: "secure_password",
                    email: "user@example.com"
                }
            },
            {
                category: "User Authentication",
                name: "User Login",
                method: "POST",
                path: "/login/",
                isPublic: true,
                description: "Authenticates an existing user and returns a JWT token. Can use either username or email.",
                bodyType: "json",
                body: {
                    username: "example_user",
                    password: "secure_password",
                    email: "user@example.com"
                }
            },
            {
                category: "User Authentication",
                name: "Forgot Password (Request OTP)",
                method: "POST",
                path: "/forgot/",
                isPublic: true,
                description: "Initiates the password recovery process by sending an OTP to the user's registered email address.",
                bodyType: "json",
                body: {
                    email: "user@example.com"
                }
            },
            {
                category: "User Authentication",
                name: "Verify OTP Code",
                method: "POST",
                path: "/forgot/code/",
                isPublic: true,
                description: "Verifies the OTP code sent to the email and returns a temporary password reset token. Pass the OTP code inside the header.",
                headers: {
                    otp: "123456"
                },
                bodyType: "json",
                body: {
                    email: "user@example.com"
                }
            },
            {
                category: "User Authentication",
                name: "Change Password (Reset)",
                method: "POST",
                path: "/verify/code/",
                isPublic: true,
                description: "Resets the user password using the verification token. Pass the verification token inside the header.",
                headers: {
                    token: "verification_token_here"
                },
                bodyType: "json",
                body: {
                    email: "user@example.com",
                    password: "new_secure_password"
                }
            },
            {
                category: "User Authentication",
                name: "Update Account Details",
                method: "PUT",
                path: "/updateacc/",
                isPublic: false,
                description: "Updates account settings like username, password, or email. (Also accepts POST method).",
                bodyType: "json",
                body: {
                    username: "updated_user",
                    password: "updated_password",
                    email: "updated_email@example.com"
                }
            },
            {
                category: "User Authentication",
                name: "Delete User Account",
                method: "DELETE",
                path: "/deleteacc/",
                isPublic: false,
                description: "Permanently deletes the user account. Requires credentials confirmation in the body.",
                bodyType: "json",
                body: {
                    username: "example_user",
                    password: "secure_password",
                    email: "user@example.com"
                }
            },
            {
                category: "File Management",
                name: "Upload File",
                method: "POST",
                path: "/uploadfile/{userid}",
                isPublic: false,
                description: "Uploads a single file to the specified directory. Note: 'filepath' is the form data key for the file payload.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "form-data",
                formFields: {
                    directory: "/"
                },
                fileFields: ["filepath"]
            },
            {
                category: "File Management",
                name: "Upload Folder",
                method: "POST",
                path: "/uploadfolder/{userid}/",
                isPublic: false,
                description: "Uploads multiple files preserving folder structure. Select one or more files to test folder upload.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "form-data",
                formFields: {
                    directory: "my_folder"
                },
                fileFields: ["files"]
            },
            {
                category: "File Management",
                name: "Download File/Folder",
                method: "GET",
                path: "/download/{userid}/",
                isPublic: false,
                description: "Downloads a file or folder (compressed as ZIP). This is a GET request that expects a JSON payload containing the filename.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "json",
                body: {
                    filename: "path/to/file_or_folder"
                }
            },
            {
                category: "File Management",
                name: "Delete File/Folder",
                method: "DELETE",
                path: "/deletefile/{userid}/",
                isPublic: false,
                description: "Deletes a file/folder or moves it to the trash.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "json",
                body: {
                    filepath: "path/to/file_or_folder",
                    trash: 1,
                    replace: 0
                }
            },
            {
                category: "File Management",
                name: "Permanently Delete from Trash",
                method: "DELETE",
                path: "/trash/{userid}/",
                isPublic: false,
                description: "Permanently removes a file/folder from the trash folder.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "json",
                body: {
                    filepath: "path/to/file_in_trash"
                }
            },
            {
                category: "File Management",
                name: "Rename File/Folder",
                method: "PUT",
                path: "/updatefile/{userid}/",
                isPublic: false,
                description: "Renames an existing file or folder in the user's directory.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "json",
                body: {
                    filename: "path/to/old_name",
                    newname: "path/to/new_name"
                }
            },
            {
                category: "File Management",
                name: "Change File Location (Move)",
                method: "PUT",
                path: "/changefilelocation/{userid}/",
                isPublic: false,
                description: "Moves a file or folder to a new destination directory.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "json",
                body: {
                    oldpath: "path/to/current_location",
                    newlocation: "path/to/new_location"
                }
            },
            {
                category: "File Management",
                name: "Search Files",
                method: "GET",
                path: "/searchfile/{userid}/{filename}/",
                isPublic: false,
                description: "Searches for files matching the specified filename query.",
                urlParams: {
                    userid: "1",
                    filename: "test"
                },
                bodyType: "none"
            },
            {
                category: "Directory Management",
                name: "Create Empty Folder",
                method: "PUT",
                path: "/createfolder/{userid}/",
                isPublic: false,
                description: "Creates an empty directory folder at the specified path.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "json",
                body: {
                    filename: "path/to/new_folder"
                }
            },
            {
                category: "Directory Management",
                name: "Get Folder Structure",
                method: "GET",
                path: "/structure/{userid}/",
                isPublic: false,
                description: "Retrieves the folder structure schema for a user. Defaults folder ID parameter to -1.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "none"
            },
            {
                category: "Directory Management",
                name: "Get Folder Structure Page",
                method: "GET",
                path: "/structure/{userid}/{folder}",
                isPublic: false,
                description: "Retrieves a specific folder structure page folder number for a user.",
                urlParams: {
                    userid: "1",
                    folder: "0"
                },
                bodyType: "none"
            },
            {
                category: "Directory Management",
                name: "Get Total Folders Count",
                method: "GET",
                path: "/folders/{userid}/",
                isPublic: false,
                description: "Retrieves the total count of folders for a user.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "none"
            },
            {
                category: "Directory Management",
                name: "Get Storage Space Stats",
                method: "GET",
                path: "/userstats/{userid}/",
                isPublic: false,
                description: "Retrieves the used space, remaining space, and update flag for a user.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "none"
            },
            {
                category: "Share & Public Access",
                name: "Generate Sharing Link",
                method: "POST",
                path: "/access/{userid}/",
                isPublic: false,
                description: "Generates a public verification link with an expiration time for a file/folder.",
                urlParams: {
                    userid: "1"
                },
                bodyType: "json",
                body: {
                    filepath: "path/to/file_or_folder",
                    time: 604800
                }
            },
            {
                category: "Share & Public Access",
                name: "Access Shared Resource",
                method: "GET",
                path: "/share/{userid}/{filesharing}/{time}/{tooken}",
                isPublic: true,
                description: "Public endpoint to retrieve a shared file or directory. Needs the exact time and tooken parameters.",
                urlParams: {
                    userid: "1",
                    filesharing: "base64_encoded_path",
                    time: "1783626681",
                    tooken: "verification_token"
                },
                bodyType: "none"
            }
        ];

        let selectedEndpointIndex = 0;

        // Init App
        window.addEventListener('DOMContentLoaded', () => {
            // Set Default Base URL
            document.getElementById('global-base-url').value = window.location.origin;
            
            renderSidebar();
            selectEndpoint(0);

            // Search Bar Filter
            document.getElementById('search-bar').addEventListener('input', (e) => {
                renderSidebar(e.target.value);
            });

            // Global User ID and Auth token changes
            document.getElementById('global-userid').addEventListener('input', () => {
                if (selectedEndpointIndex !== null) selectEndpoint(selectedEndpointIndex);
            });
            document.getElementById('global-token').addEventListener('input', () => {
                if (selectedEndpointIndex !== null) selectEndpoint(selectedEndpointIndex);
            });
        });

        function renderSidebar(filter = '') {
            const container = document.getElementById('endpoint-list-container');
            container.innerHTML = '';

            const groups = {};
            endpoints.forEach((ep, index) => {
                if (filter && !ep.name.toLowerCase().includes(filter.toLowerCase()) && !ep.path.toLowerCase().includes(filter.toLowerCase())) {
                    return;
                }
                if (!groups[ep.category]) {
                    groups[ep.category] = [];
                }
                groups[ep.category].push({ ...ep, index });
            });

            for (const [category, list] of Object.entries(groups)) {
                const groupDiv = document.createElement('div');
                groupDiv.className = 'category-group';
                
                const title = document.createElement('div');
                title.className = 'category-title';
                title.textContent = category;
                groupDiv.appendChild(title);

                list.forEach(ep => {
                    const item = document.createElement('div');
                    item.className = `endpoint-item ${selectedEndpointIndex === ep.index ? 'active' : ''}`;
                    item.onclick = () => selectEndpoint(ep.index);

                    const badge = document.createElement('span');
                    badge.className = `method-badge ${ep.method.toLowerCase()}`;
                    badge.textContent = ep.method;
                    
                    const name = document.createElement('span');
                    name.className = 'endpoint-name';
                    name.textContent = ep.name;

                    item.appendChild(badge);
                    item.appendChild(name);
                    groupDiv.appendChild(item);
                });

                container.appendChild(groupDiv);
            }
        }

        function selectEndpoint(index) {
            selectedEndpointIndex = index;
            
            // Highlight active sidebar item
            const items = document.querySelectorAll('.endpoint-item');
            items.forEach((item, i) => {
                item.classList.remove('active');
            });
            // Re-render sidebar to apply active class easily
            renderSidebar(document.getElementById('search-bar').value);

            const ep = endpoints[index];
            const detailPanel = document.getElementById('detail-panel');
            
            // Get global variables
            const globalUserId = document.getElementById('global-userid').value;
            const globalToken = document.getElementById('global-token').value;

            // Generate Path with parameters replaced
            let displayPath = ep.path;
            const urlParamInputs = [];
            
            if (ep.urlParams) {
                Object.keys(ep.urlParams).forEach(param => {
                    let defaultVal = ep.urlParams[param];
                    if ((param.toLowerCase() === 'userid') && globalUserId) {
                        defaultVal = globalUserId;
                    }
                    displayPath = displayPath.replace(`{${param}}`, defaultVal);
                    
                    urlParamInputs.push({
                        name: param,
                        value: defaultVal,
                        description: `URL path parameter {${param}}`
                    });
                });
            }

            // Generate HTML for details
            let html = `
                <div class="endpoint-title-section">
                    <h2>${ep.name}</h2>
                    <span class="auth-badge ${ep.isPublic ? 'public' : 'private'}">
                        ${ep.isPublic ? 'Public Endpoint' : 'Requires Auth'}
                    </span>
                </div>
                
                <div class="full-path-container">
                    <span class="full-path-method ${ep.method.toLowerCase()}">${ep.method}</span>
                    <span class="full-path-url" id="endpoint-rendered-url">${displayPath}</span>
                    <svg class="badge-copy" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" onclick="navigator.clipboard.writeText(document.getElementById('endpoint-rendered-url').textContent)">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2" />
                    </svg>
                </div>

                <div class="endpoint-desc">${ep.description}</div>
            `;

            // Render URL Path parameters
            if (urlParamInputs.length > 0) {
                html += `
                    <div class="section-header">Path Parameters</div>
                    <table class="param-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Value</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                urlParamInputs.forEach(param => {
                    html += `
                        <tr>
                            <td class="param-name">${param.name}</td>
                            <td>
                                <input type="text" class="param-input url-path-param-input" data-paramname="${param.name}" value="${param.value}" oninput="updateUrlPreview()">
                            </td>
                            <td class="param-desc">${param.description}</td>
                        </tr>
                    `;
                });
                html += `</tbody></table>`;
            }

            // Render Request Headers
            const headerList = [];
            if (!ep.isPublic) {
                headerList.push({
                    name: 'auth',
                    value: globalToken,
                    description: 'JWT Authentication token (Copied from Global Config above)'
                });
            }
            if (ep.headers) {
                Object.keys(ep.headers).forEach(h => {
                    headerList.push({
                        name: h,
                        value: ep.headers[h],
                        description: `Custom header required for this operation`
                    });
                });
            }

            if (headerList.length > 0) {
                html += `
                    <div class="section-header">Headers</div>
                    <table class="param-table">
                        <thead>
                            <tr>
                                <th>Header Key</th>
                                <th>Value</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                headerList.forEach(header => {
                    html += `
                        <tr>
                            <td class="param-name">${header.name}</td>
                            <td>
                                <input type="text" class="param-input header-param-input" data-headername="${header.name}" value="${header.value}">
                            </td>
                            <td class="param-desc">${header.description}</td>
                        </tr>
                    `;
                });
                html += `</tbody></table>`;
            }

            // Render Body Payload section
            if (ep.bodyType === 'json') {
                html += `
                    <div class="section-header">JSON Body Payload</div>
                    <div class="json-editor-container">
                        <textarea class="json-editor" id="json-body-textarea">${JSON.stringify(ep.body, null, 4)}</textarea>
                    </div>
                `;
            } else if (ep.bodyType === 'form-data') {
                html += `
                    <div class="section-header">Form Data Fields</div>
                    <table class="param-table">
                        <thead>
                            <tr>
                                <th>Field Key</th>
                                <th>Value / File</th>
                                <th>Type</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                if (ep.formFields) {
                    Object.keys(ep.formFields).forEach(key => {
                        html += `
                            <tr>
                                <td class="param-name">${key}</td>
                                <td>
                                    <input type="text" class="param-input form-data-field-input" data-fieldkey="${key}" value="${ep.formFields[key]}">
                                </td>
                                <td><span class="param-type">text</span></td>
                            </tr>
                        `;
                    });
                }
                if (ep.fileFields) {
                    ep.fileFields.forEach(key => {
                        const isMultiple = key === 'files';
                        html += `
                            <tr>
                                <td class="param-name">${key}</td>
                                <td>
                                    <input type="file" class="form-data-file-input" data-fieldkey="${key}" ${isMultiple ? 'multiple' : ''}>
                                </td>
                                <td><span class="param-type">file${isMultiple ? '[]' : ''}</span></td>
                            </tr>
                        `;
                    });
                }
                html += `</tbody></table>`;
            }

            // Send Request Button
            html += `
                <button class="btn-send" onclick="sendApiRequest()" id="btn-submit-request">
                    <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Send Request
                </button>
            `;

            detailPanel.innerHTML = html;
        }

        function updateUrlPreview() {
            const ep = endpoints[selectedEndpointIndex];
            let displayPath = ep.path;
            
            const inputs = document.querySelectorAll('.url-path-param-input');
            inputs.forEach(input => {
                const param = input.getAttribute('data-paramname');
                const val = input.value;
                displayPath = displayPath.replace(`{${param}}`, val);
            });

            document.getElementById('endpoint-rendered-url').textContent = displayPath;
        }

        async function sendApiRequest() {
            const ep = endpoints[selectedEndpointIndex];
            const btn = document.getElementById('btn-submit-request');
            const consoleInner = document.getElementById('response-panel');
            
            btn.disabled = true;
            btn.innerHTML = `
                <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="animate-spin" style="animation: spin 1s linear infinite;">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 7.89H18" />
                </svg>
                Executing...
            `;

            // Prepare URL
            const baseUrl = document.getElementById('global-base-url').value || window.location.origin;
            let displayPath = ep.path;
            
            const pathInputs = document.querySelectorAll('.url-path-param-input');
            pathInputs.forEach(input => {
                const param = input.getAttribute('data-paramname');
                displayPath = displayPath.replace(`{${param}}`, input.value);
            });

            const requestUrl = baseUrl.replace(/\\/$/, '') + displayPath;

            // Prepare Headers
            const headers = {};
            const headerInputs = document.querySelectorAll('.header-param-input');
            headerInputs.forEach(input => {
                const name = input.getAttribute('data-headername');
                if (input.value) {
                    headers[name] = input.value;
                }
            });

            // Prepare Body
            let body = null;
            if (ep.bodyType === 'json') {
                headers['Content-Type'] = 'application/json';
                const jsonText = document.getElementById('json-body-textarea').value;
                try {
                    body = JSON.stringify(JSON.parse(jsonText));
                } catch(e) {
                    alert('Invalid JSON in Body Payload');
                    btn.disabled = false;
                    btn.innerHTML = 'Send Request';
                    return;
                }
            } else if (ep.bodyType === 'form-data') {
                const formData = new FormData();
                
                const formInputs = document.querySelectorAll('.form-data-field-input');
                formInputs.forEach(input => {
                    const key = input.getAttribute('data-fieldkey');
                    formData.append(key, input.value);
                });

                const fileInputs = document.querySelectorAll('.form-data-file-input');
                fileInputs.forEach(input => {
                    const key = input.getAttribute('data-fieldkey');
                    if (input.files.length > 0) {
                        for (let i = 0; i < input.files.length; i++) {
                            formData.append(key, input.files[i]);
                        }
                    }
                });
                body = formData;
            }

            const startTime = performance.now();
            
            try {
                const response = await fetch(requestUrl, {
                    method: ep.method,
                    headers: headers,
                    body: body
                });

                const endTime = performance.now();
                const duration = Math.round(endTime - startTime);
                
                const isSuccess = response.status >= 200 && response.status < 300;
                
                // Get Response Data
                const contentType = response.headers.get('content-type') || '';
                let resultText = '';
                
                if (contentType.includes('application/json')) {
                    const json = await response.json();
                    
                    // If login/createaccount token is received, update global auth token box!
                    if (json.return && (ep.name === 'User Login' || ep.name === 'Create User Account')) {
                        document.getElementById('global-token').value = json.return;
                        if (json.userid) {
                            document.getElementById('global-userid').value = json.userid;
                        }
                    }
                    resultText = JSON.stringify(json, null, 4);
                } else if (contentType.includes('text/') || contentType.includes('javascript') || contentType.includes('html')) {
                    resultText = await response.text();
                } else {
                    // Blob download
                    const blob = await response.blob();
                    resultText = `Binary Data Received: ${blob.type} (${blob.size} bytes)\\n`;
                    
                    const contentDisposition = response.headers.get('Content-Disposition');
                    if (contentDisposition) {
                        resultText += `Content-Disposition: ${contentDisposition}\\n`;
                    }
                    resultText += `Filesize Header: ${response.headers.get('filesize') || 'None'}\\n`;
                    resultText += `Filetype Header: ${response.headers.get('filetype') || 'None'}\\n`;
                }

                // Render Response Console
                renderResponseConsole(response.status, response.statusText, duration, resultText);

            } catch (error) {
                const endTime = performance.now();
                const duration = Math.round(endTime - startTime);
                renderResponseConsole(0, 'Network Error / Fetch Failed', duration, error.message);
            }

            btn.disabled = false;
            btn.innerHTML = `
                <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Send Request
            `;
        }

        function renderResponseConsole(status, statusText, duration, data) {
            const container = document.getElementById('response-panel');
            const isSuccess = status >= 200 && status < 300;
            
            let statusClass = 'status-success';
            if (status === 0 || status >= 400) {
                statusClass = 'status-error';
            }

            container.innerHTML = `
                <div class="section-header">Response Console</div>
                <div class="response-header-stats">
                    <div class="stat-badge ${statusClass}">
                        <span>STATUS:</span> ${status} ${statusText}
                    </div>
                    <div class="stat-badge">
                        <span>TIME:</span> ${duration} ms
                    </div>
                </div>
                <pre class="response-viewer" id="response-code-block">${escapeHtml(data)}</pre>
            `;
        }

        function escapeHtml(unsafe) {
            return unsafe
                 .replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
        }
    </script>
    
    <style>
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    </style>
</body>
</html>
"""

@docsbp.route("/docs", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE)
