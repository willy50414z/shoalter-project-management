from util import JiraUtil, NotionUtil

#NotionUtil.createPage('EER-XXX', 'title','task','willy.cheng@shoalter.com')
#print(NotionUtil.findByTicketLike('MS-2831'))

excludeTicket = ["MS-1490","MS-1308"]

def createNotionTaskFromJira():
    # fetch JIRA incomplete ticket
    issues = JiraUtil.getIncompletedTask()

    #for issue in issues:
    #    print(issue.key)iddaa--ddd  sda1231

    # check is ticket exist in notion
    for issue in issues:
        # only create subtask or task without subtask
        if issue.fields.issuetype.name != '大型工作' and not issue.key.startswith('BUILD') and (issue.fields.issuetype.subtask or 0 == len(issue.fields.subtasks)):
            print(f"check notion contains ticket or not, ticket[{issue.key}]")
            notionItemList = NotionUtil.findByTicketLike(issue.key)
            
            if 0 == len(notionItemList):
                #get default assignee
                displayName = 'TW - IT - BE - Willy Cheng'
                if issue.fields.assignee is not None:
                    displayName = issue.fields.assignee.displayName
                    
                #exclude dead ticket
                if issue.key in excludeTicket:
                    print(f"[{issue.key}] is excluded ticket")
                    continue
                    
                if issue.fields.issuetype.subtask:
                    print(f"ticket is not exist. Start to create ticket to notion, ticket[{issue.key}]")
                    NotionUtil.createPage(issue.key, issue.fields.summary, issue.fields.parent.key, displayName)
                else:
                    NotionUtil.createPage(issue.key, issue.fields.summary, issue.key, displayName)
            else:
                #notion exist => update ticket info
                print(f"ticket is exist, ticket[{issue.key}]")
# create notion item

# update notion status


if __name__=='__main__':
    createNotionTaskFromJira()
    NotionUtil.deleteOutOfDateTask()
    # print(NotionUtil.findByTicketLike("xxx"))

    # notionItems = NotionUtil.findAllReleases()
    # for notionItem in notionItems:
    #     print(notionItem["id"])
    #     print(notionItem["properties"]["Name"]["title"][0]["text"]["content"])
    #     print(notionItem["properties"]["Release Date"]["date"]["start"])
    #     for releaseTicket in notionItem["properties"]["ReleaseTickets"]["multi_select"]:
    #         print(releaseTicket["name"])
