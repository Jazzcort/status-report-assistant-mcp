# Status Report Assistant MCP

## Set up your environment

### Prerequisites

#### Mandatory
- **uv**: Follow the installation guide [here](https://docs.astral.sh/uv/getting-started/installation)

#### Optional (If you want the model to create the draft email for you)
- **OAuth 2.0 Credentials**: You need to have the OAuth 2.0 credential json file which can be created at Google Could Console
  - Steps:
    - Create a project and enable using Gmail API
    - Create an OAuth 2.0 client

      ![step-1: create OAuth 2.0 client](https://github.com/Jazzcort/status-report-assistant-mcp/blob/main/media/oauth2-step1.png)

    - Select Application type

      ![step-2: select application type](https://github.com/Jazzcort/status-report-assistant-mcp/blob/main/media/oauth2-step2.png)

    - Download the json credentials file

      ![step-3: download the json credentials file](https://github.com/Jazzcort/status-report-assistant-mcp/blob/main/media/oauth2-step3.png)

- **.env**: You need to have an `.env` file containing two environment variables with specific names 
```text
GOOGLE_OAUTH2_CREDENTIALS="<Path of Google OAuth 2.0 credentials>"
CREDENTIAL_TOKEN="<Where you want to store the credentials for using Gmail API>"
```


## Configuration 

### Cursor

```json
{
  "mcpServers": {
    "status-report-mcp": {
      "command": "uvx",
      "args": [
        "--env-file",
        "<path of .env>",
        "--from",
        "git+https://github.com/Jazzcort/status-report-assistant-mcp",
        "mcp-serve"
      ]
    }
  }
}
```

### Continue

```yaml

mcpServers:
  - name: Status Report Assistant
    command: uvx
    args:
      - "--env-file"
      - "<path of .env>"
      - "--from"
      - "git+https://github.com/Jazzcort/status-report-assistant-mcp"
      - "mcp-serve"
```

## Example Prompt

### Gather the work log

```text
Can you gather the work log for <directory/directories you want the work log to be generated from> directory from 10 days ago till now and summarize it?

Add a link that refers to each commit and make the summary a bullet point style with each commit as a seperate point

Please combine the duplicate commits into one.

Today is 2025-07-16.

```

### Create a draft email

```text
Can you create a draft email with the work log summary as the content, proper subject, and <recipient email address> as a recipient?
```

