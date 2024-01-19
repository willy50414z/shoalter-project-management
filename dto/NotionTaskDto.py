class NotionTaskDto:
    def __init__(self, item):
        self.notionItem = item

    def getTitle(self):
        return self.notionItem["properties"]["Name"]["title"][0]["plain_text"]

    def getProjectName(self):
        return self.notionItem["properties"]["Project"]["select"]["name"]

    def getTicketUrl(self):
        return self.notionItem["properties"]["Ticket"]["url"]

    def getTicketUrl(self):
        return self.notionItem["properties"]["Ticket"]["url"]

    def getAttachmentList(self):
        attachmentList = []
        for attachment in self.notionItem["properties"]["attachment"]["multi_select"]:
            attachmentList.append(attachment["name"])
        return attachmentList