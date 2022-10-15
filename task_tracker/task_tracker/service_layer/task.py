from task_tracker.domain import event, model
from task_tracker.service_layer.unit_of_work import AbstractUnitOfWork

ASSIGNABLE_ROLES = [model.UserRole.manager, model.UserRole.accountant]


async def get_tasks(
    uow: AbstractUnitOfWork,
    status: model.TaskStatus | None = None,
    user_id: model.UserPublicID | None = None,
) -> list[model.Task]:
    kwargs = {}

    if user_id:
        kwargs["user_id"] = user_id

    if status:
        kwargs["status"] = status

    tasks = await uow.tasks.get_tasks(**kwargs)
    return tasks


async def create_task(
    uow: AbstractUnitOfWork, description: str, jira_id: model.TaskJiraID | None
) -> model.Task:
    user = await uow.users.get_random_user(roles=ASSIGNABLE_ROLES)
    assert user is not None

    create_request = model.CreateTaskRequest(
        user_id=user.public_id, description=description, jira_id=jira_id
    )
    task = await uow.tasks.create_task(create_request)

    task_event = event.TaskAdded(
        description=task.description,
        public_id=task.public_id,
        status=task.status,
        user_id=task.user_id,
    )
    uow.events.append(task_event)

    await uow.commit()
    return task


async def request_task_shuffle(
    uow: AbstractUnitOfWork, user_id: model.UserPublicID
) -> None:
    shuffle_event = event.TaskShuffleRequested(user_id=user_id)
    uow.events.append(shuffle_event)

    await uow.commit()


async def shuffle_tasks(uow: AbstractUnitOfWork, *args, **kwargs) -> None:
    tasks = await uow.tasks.get_tasks(status=model.TaskStatus.open)

    for task in tasks:
        user = await uow.users.get_random_user(roles=ASSIGNABLE_ROLES)
        task.user_id = user.public_id

        uow.events.append(
            event.TaskAssigned(public_id=task.public_id, user_id=user.public_id)
        )
        await uow.tasks.update_task(task)

    await uow.commit()


async def close_task(
    uow: AbstractUnitOfWork, user_id: model.UserPublicID, task_id: model.TaskPublicID
) -> model.Task:
    task = await uow.tasks.get_task_by_id(task_id)
    assert task.user_id == user_id

    task.status = model.TaskStatus.closed

    close_event = event.TaskClosed(public_id=task.public_id)
    uow.events.append(close_event)

    await uow.tasks.update_task(task)
    return task


EVENT_HANDLERS = {
    event.TaskShuffleRequested: [shuffle_tasks],
}
